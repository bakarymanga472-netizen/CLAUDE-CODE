#!/usr/bin/env python3
"""Voix off naturelle (mode recommandé pour publier) : Chatterbox multilingue + vraie voix de référence.

Usage : python3 voix_naturelle.py "Texte" sortie.wav [--reference ma_voix.wav] [--timings phrases.json]
                                  [--mots-min 145] [--energie 0.6]

Pourquoi : Kokoro aplatit la mélodie de la voix (écart-type 2,86 demi-tons contre 3,45 pour la même
comédienne enregistrée), d'où l'effet « robot ». Chatterbox, guidé par un vrai enregistrement, monte à 3,96,
dans la fourchette de 4 narrateurs humains (2,96 à 4,84). Mesures du 2026-11-15, voir SKILL.md.

Étapes : une phrase à la fois ; chaque phrase est réécoutée par Whisper et regénérée (4 essais max) si un
mot est faux ou répété ; accélération sans changer la hauteur (Rubber Band) jusqu'au débit visé ;
pauses variables ; mastering de voix.py (-14 LUFS, crête -1,5 dBFS).

Voix de référence par défaut : 4 phrases du corpus SIWIS (comédienne enregistrée pour la synthèse vocale,
licence CC BY 4.0 → créditer « Voix : SIWIS French Speech Synthesis Database, CC BY 4.0 »).
Mieux : --reference avec 10 à 20 s de TA voix (ou d'une personne qui a donné son accord écrit).
Ne jamais cloner la voix d'un créateur ou d'une personne sans son accord.

Installation (une fois, ~4 Go avec les modèles) :
  pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
  pip install chatterbox-tts faster-whisper num2words remotezip pedalboard pyloudnorm soundfile
Sur CPU : environ 30 s de calcul par phrase.
"""
import argparse, difflib, json, pathlib, re, sys

CACHE = pathlib.Path.home() / ".cache" / "voix-off"
SIWIS_ZIP = "https://datashare.ed.ac.uk/bitstreams/64de089d-0ad5-45cb-a1c0-b6b39ecf6225/download"
SIWIS_FICHIERS = [f"SiwisFrenchSpeechSynthesisDatabase/wavs/part1/neut_parl_s01_000{i}.wav" for i in range(1, 5)]


def reference_siwis():
    """Extrait 4 phrases du corpus SIWIS (2,9 Go) par requêtes partielles, sans tout télécharger."""
    import numpy as np, librosa, soundfile as sf
    from remotezip import RemoteZip
    ref = CACHE / "siwis_ref.wav"
    if ref.exists():
        return str(ref)
    CACHE.mkdir(parents=True, exist_ok=True)
    parts = []
    with RemoteZip(SIWIS_ZIP) as z:
        for n in SIWIS_FICHIERS:
            z.extract(n, CACHE / "siwis")
            y, _ = librosa.load(CACHE / "siwis" / n, sr=24000)
            parts += [librosa.effects.trim(y, top_db=35)[0], np.zeros(7200, dtype=np.float32)]
    sf.write(ref, np.concatenate(parts), 24000)
    return str(ref)


def normalise(s):
    from num2words import num2words
    s = re.sub(r"(\d)[\s.](\d{3})", r"\1\2", s)
    s = re.sub(r"(\d+)\s*h\b", lambda m: num2words(int(m.group(1)), lang="fr") + " heures", s)
    s = re.sub(r"\d+", lambda m: num2words(int(m.group()), lang="fr"), s).replace("€", " euros ").replace("%", " pour cent ")
    s = s.lower().replace("'", " ").replace("’", " ").replace("-", "")
    return [("euro" if m == "euros" else m) for m in re.sub(r"[^\w\s]", " ", s).split()]


def taux_erreur(ref, hyp):
    d = list(range(len(hyp) + 1))
    for i, a in enumerate(ref, 1):
        p, d[0] = d[0], i
        for j, b in enumerate(hyp, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (a != b))
    return d[-1] / max(len(ref), 1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("texte")
    p.add_argument("sortie")
    p.add_argument("--reference", help="10-20 s de voix à imiter (par défaut : SIWIS, CC BY 4.0)")
    p.add_argument("--timings", help="écrit le début/fin de chaque phrase (s) pour caler les sous-titres")
    p.add_argument("--mots-min", type=float, default=145, help="débit visé, pauses comprises (140-150 conseillé)")
    p.add_argument("--energie", type=float, default=0.6, help="expressivité Chatterbox (0,5 calme, 0,7 très animé)")
    p.add_argument("--prononcer", action="append", default=[], metavar="MOT=SON",
                   help="corrige un mot mal prononcé, ex. --prononcer \"Africa Corps=Afrika Kor\" (audio seulement)")
    a = p.parse_args()

    import numpy as np, torch, librosa, soundfile as sf
    from faster_whisper import WhisperModel
    from pedalboard import time_stretch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from voix import mastering

    ref = a.reference or reference_siwis()
    asr = WhisperModel("small", device="cpu", compute_type="int8")
    tts = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    sr = tts.sr
    phrases = [m.strip() for m in re.findall(r"[^.?!]+[.?!]?", a.texte) if m.strip()]

    regles = [r.split("=", 1) for r in a.prononcer]

    def prononce(s):
        for mot, son in regles:
            s = re.sub(rf"\b{re.escape(mot)}\b", son, s)
        return s

    import hashlib
    cache_seg = CACHE / "segments"
    cache_seg.mkdir(parents=True, exist_ok=True)
    empreinte_ref = hashlib.sha1(pathlib.Path(ref).read_bytes()).hexdigest()[:10]
    segments = []
    for i, ph in enumerate(phrases):
        dit = prononce(ph)
        cle = hashlib.sha1(f"v2|{dit}|{empreinte_ref}|{a.energie}".encode()).hexdigest()[:16]
        if (cache_seg / f"{cle}.npy").exists():  # phrase déjà générée et vérifiée : on la réutilise
            segments.append(np.load(cache_seg / f"{cle}.npy"))
            print(f"{i}: (cache) {ph}", file=sys.stderr)
            continue
        meilleur = None
        for essai in range(4):
            torch.manual_seed(100 * i + essai)
            y = tts.generate(dit, language_id="fr", audio_prompt_path=ref, exaggeration=a.energie, cfg_weight=0.5)
            y = librosa.effects.trim(y.squeeze(0).numpy(), top_db=35)[0]
            segs_asr = asr.transcribe(librosa.resample(y, orig_sr=sr, target_sr=16000), language="fr",
                                      beam_size=5, word_timestamps=True)[0]
            mots = [(w.word, w.end) for s in segs_asr for w in s.words]
            hyp = "".join(w for w, _ in mots)
            # années et grands nombres ; « 3 560 » et « 3560 » comptent pour le même nombre
            grands = lambda s: [n for n in re.findall(r"\d+", re.sub(r"(\d)[\s\u202f.](?=\d{3}\b)", r"\1", s)) if len(n) >= 3]
            textes_ref = [" " + " ".join(normalise(x)) + " " for x in (ph, dit)]

            def erreur(h):
                e = min(taux_erreur(normalise(ph), normalise(h)), taux_erreur(normalise(dit), normalise(h)))
                # une date ou un nombre faux est grave (« 1854 » au lieu de « 1884 » ne compte que pour un mot) :
                # chaque nombre que Whisper écrit en chiffres doit se retrouver, en toutes lettres, dans le texte
                # (le texte peut l'écrire en chiffres, « 3 560 », ou en lettres, « trente-cinq mille »)
                faux = [n for n in grands(h) if not any(" " + " ".join(normalise(n)) + " " in r for r in textes_ref)]
                return max(e, 0.5) if faux else e
            e = erreur(hyp)
            # son parasite après la fin du texte (Chatterbox ajoute parfois une « queue ») : on coupe
            # On ne coupe que si le mot entendu à cet endroit est bien le dernier mot du texte : sinon un nom
            # transcrit en deux morceaux (« Turenge » → « tu » + « renge ») serait coupé au milieu.
            n_ref, cumul, dernier = len(normalise(dit)), 0, normalise(dit)[-1]
            for k, (w, fin) in enumerate(mots):
                cumul += len(normalise(w))
                if cumul >= n_ref:
                    entendu = (normalise(w) or [""])[-1]
                    complet = difflib.SequenceMatcher(None, entendu, dernier).ratio() >= 0.75
                    if complet and any(normalise(x) for x, _ in mots[k + 1:]):
                        hyp_c = "".join(x for x, _ in mots[:k + 1])
                        if erreur(hyp_c) < e:
                            y, hyp, e = y[:int((fin + 0.15) * sr)], hyp_c + " [queue parasite coupée]", erreur(hyp_c)
                    break
            if meilleur is None or e < meilleur[0]:
                meilleur = (e, y, hyp)
            if e <= 0.10:
                break
        e, y, hyp = meilleur
        print(f"{i}: {e:.0%} d'erreur | {hyp.strip()}", file=sys.stderr)
        if e > 0.10:
            print(f"   ⚠ phrase {i} encore imparfaite : reformuler « {ph} » ou utiliser --prononcer", file=sys.stderr)
        else:
            np.save(cache_seg / f"{cle}.npy", y)
        segments.append(y)

    # pauses irrégulières comme à l'oral
    pauses = []
    for i, ph in enumerate(phrases[:-1]):
        suivante = phrases[i + 1]
        if ph.endswith("?"):
            pauses.append(0.55)
        elif i == len(phrases) - 2:
            pauses.append(0.52)
        elif len(ph.split()) <= 6 and len(suivante.split()) <= 6:
            pauses.append(0.24)
        else:
            pauses.append(0.30 + 0.01 * min(len(suivante.split()), 12))

    # accélération (sans changer la hauteur) jusqu'au débit visé, bornée pour rester naturelle
    mots = sum(len(ph.split()) for ph in phrases)
    duree = sum(len(s) for s in segments) / sr + sum(pauses)
    facteur = min(max(a.mots_min / (60 * mots / duree), 1.0), 1.22)
    morceaux, timings, t = [], [], 0.0
    for i, s in enumerate(segments):
        if facteur > 1.001:
            s = time_stretch(s[None, :].astype(np.float32), sr, stretch_factor=facteur, high_quality=True)[0]
        timings.append({"texte": phrases[i], "debut": round(t, 3), "fin": round(t + len(s) / sr, 3)})
        morceaux.append(s)
        t += len(s) / sr
        if i < len(pauses):
            morceaux.append(np.zeros(int(pauses[i] * sr), dtype=np.float32))
            t += pauses[i]
    y = mastering(np.concatenate(morceaux), sr)
    sf.write(a.sortie, y, sr)
    if a.timings:
        pathlib.Path(a.timings).write_text(json.dumps(timings, ensure_ascii=False, indent=1))
    print(f"{a.sortie} : {len(y) / sr:.1f} s, accéléré x{facteur:.2f}, {60 * mots / (len(y) / sr):.0f} mots/min")


if __name__ == "__main__":
    main()
