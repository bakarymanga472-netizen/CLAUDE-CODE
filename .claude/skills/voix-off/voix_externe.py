#!/usr/bin/env python3
"""Prépare une narration générée ailleurs (ex. ElevenLabs via Higgsfield) pour une vidéo Remotion.

Usage : python3 voix_externe.py narration.mp3 "Texte exact lu" public/voix.wav --timings src/phrases.json

- Retrouve le début et la fin de chaque phrase avec Whisper (horodatage par mot), pour caler sous-titres et scènes.
- Applique le même mastering que les autres modes (voix.py : -14 LUFS, crête -1,5 dBFS).
- Affiche ce que Whisper a entendu, phrase par phrase, pour repérer un mot mal prononcé avant le rendu.
"""
import argparse, difflib, json, pathlib, re, sys, unicodedata


def norme(m):
    m = unicodedata.normalize("NFD", m.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in m if unicodedata.category(c) != "Mn"))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("audio")
    a.add_argument("texte")
    a.add_argument("sortie")
    a.add_argument("--timings")
    a.add_argument("--modele", default="small", help="modèle Whisper (medium = plus sûr pour les noms propres)")
    o = a.parse_args()

    import librosa, numpy as np, soundfile as sf
    from faster_whisper import WhisperModel
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from voix import mastering

    sr = 24000
    y, _ = librosa.load(o.audio, sr=sr, mono=True)
    y16 = librosa.resample(y, orig_sr=sr, target_sr=16000)
    segs, _ = WhisperModel(o.modele, device="cpu", compute_type="int8").transcribe(y16, language="fr", word_timestamps=True, beam_size=5)
    # les mots composés (« Nouvelle-Zélande ») sont découpés au trait d'union des deux côtés
    entendus = [(x, w.start, w.end) for s in segs for w in s.words for x in re.split(r"[-\s]+", w.word.strip()) if norme(x)]

    phrases = [p.strip() for p in re.findall(r"[^.?!]+[.?!]?", o.texte) if p.strip()]
    mots = [(i, x) for i, p in enumerate(phrases) for m in p.split() for x in m.split("-") if norme(x)]
    sm = difflib.SequenceMatcher(None, [norme(m) for _, m in mots], [norme(w[0]) for w in entendus], autojunk=False)
    cale = {}
    for b in sm.get_matching_blocks():
        for k in range(b.size):
            cale[b.a + k] = entendus[b.b + k]

    duree = len(y) / sr
    debuts, comptes = [], []
    for i, p in enumerate(phrases):
        idx = [k for k, (ph, _) in enumerate(mots) if ph == i]
        trouves = [cale[k] for k in idx if k in cale]
        comptes.append((len(trouves), len(idx)))
        debuts.append(trouves[0][1] if trouves else None)
    for i in range(len(debuts)):  # phrase non retrouvée : placée juste après la précédente
        if debuts[i] is None:
            debuts[i] = (debuts[i - 1] + 0.5) if i else 0.0
    timings = []
    for i, p in enumerate(phrases):
        borne = debuts[i + 1] if i + 1 < len(phrases) else duree + 1
        dedans = [w for w in entendus if debuts[i] - 0.05 <= w[1] < borne - 0.05]
        f = max((w[2] for w in dedans), default=debuts[i] + 0.3 * len(p.split()))
        timings.append({"texte": p, "debut": round(debuts[i], 3), "fin": round(min(f, duree), 3)})
        print(f"{i}: {comptes[i][0]}/{comptes[i][1]} mots retrouvés | {' '.join(w[0] for w in dedans)}", file=sys.stderr)

    sf.write(o.sortie, mastering(y, sr), sr)
    if o.timings:
        pathlib.Path(o.timings).write_text(json.dumps(timings, ensure_ascii=False, indent=1))
    print(f"{o.sortie} : {duree:.1f} s, {len(phrases)} phrases", file=sys.stderr)


if __name__ == "__main__":
    main()
