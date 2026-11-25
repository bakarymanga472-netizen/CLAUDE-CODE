#!/usr/bin/env python3
"""Cale chaque mot du texte sur la voix (Whisper, horodatage par mot) et calcule les moments clés.

Usage : python3 prep_enquete.py texte.txt phrases.json voix.wav DOSSIER_SORTIE
        python3 prep_enquete.py texte.txt --estimation DOSSIER_SORTIE   (sans voix : durées estimées)
Écrit phrases-enquete.json, mots-enquete.json, evts-enquete.json.
"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

MOTS_CLES = {"1985", "auckland", "bombes", "rainbow", "warrior", "greenpeace", "pereira", "noye", "mururoa", "nucleaires",
             "suisses", "turenge", "mafart", "prieur", "agents", "secrets", "mois", "monde", "troisieme", "plongeurs", "hernu",
             "demissionne", "ordre", "qui", "vingt", "manuscrite", "partie", "abonne-toi"}

# moment clé -> (phrase, mot) ; l'image et le son se calent sur le début de ce mot
EVTS = {"rainbow": (2, "rainbow"), "b1": (2, "explosent"), "noye": (3, "noye"), "nucleaires": (4, "nucleaires"),
        "mururoa": (4, "mururoa"), "touristes": (5, "touristes"), "faux": (6, "vrais"), "mafart": (6, "alain"),
        "prieur": (6, "dominique"), "agents": (7, "agents"), "secrets": (7, "secrets"), "mois": (8, "mois"),
        "monde": (9, "monde"), "troisieme": (9, "troisieme"), "plongeurs": (9, "plongeurs"), "demission": (10, "demissionne"),
        "premier": (11, "premier"), "ils": (11, "ils"), "qui": (12, "qui"), "vingt": (13, "vingt"),
        "manuscrite": (13, "manuscrite"), "chef": (13, "chef"), "publiee": (13, "publiee"), "partie2": (14, "partie"),
        "abonne": (14, "abonne-toi")}


def norme(m):
    m = unicodedata.normalize("NFD", m.lower())
    m = "".join(ch for ch in m if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9'-]", "", m).strip("'-")


def decoupe(texte):
    return [p.strip() for p in re.findall(r"[^.?!]+[.?!]?", texte) if p.strip()]


def poids(m):
    return max(1, len(re.findall(r"[aeiouyàâéèêëîïôûù]+", m.lower())) + (6 if m.strip(".,").isdigit() and len(m) > 2 else 0))


def repartir(mots, d, f):
    """Répartit [d, f] entre les mots au prorata de leurs syllabes approximatives."""
    tot = sum(poids(m) for m in mots)
    t, out = d, []
    for m in mots:
        dt = (f - d) * poids(m) / tot
        out.append([t, t + dt])
        t += dt
    return out


def main():
    a = sys.argv[1:]
    texte = Path(a[0]).read_text().strip()
    sorties = Path(a[-1])
    morceaux = decoupe(texte)
    if a[1] == "--estimation":
        phrases, t = [], 0.0
        for p in morceaux:
            d = len(p.split()) * 0.4
            phrases.append({"texte": p, "debut": round(t, 3), "fin": round(t + d, 3)})
            t += d + 0.35
        mots_whisper = None
    else:
        phrases = json.loads(Path(a[1]).read_text())
        import librosa
        from faster_whisper import WhisperModel
        audio, _ = librosa.load(a[2], sr=16000, mono=True)
        segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(audio, language="fr", word_timestamps=True, beam_size=5)
        mots_whisper = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    assert len(phrases) == len(morceaux), (len(phrases), len(morceaux))

    mots, cales = [], 0
    for i, ph in enumerate(phrases):
        ms = morceaux[i].split()
        temps = repartir(ms, ph["debut"], ph["fin"])
        if mots_whisper:
            ww = [w for w in mots_whisper if w[1] >= ph["debut"] - 0.2 and w[2] <= ph["fin"] + 0.3]
            sm = difflib.SequenceMatcher(None, [norme(m) for m in ms], [norme(w[0]) for w in ww], autojunk=False)
            trouve = {}
            for bloc in sm.get_matching_blocks():
                for k in range(bloc.size):
                    trouve[bloc.a + k] = ww[bloc.b + k]
            cales += len(trouve)
            # les mots non retrouvés se répartissent entre leurs voisins retrouvés
            j = 0
            while j < len(ms):
                if j in trouve:
                    temps[j] = [trouve[j][1], trouve[j][2]]
                    j += 1
                    continue
                k = j
                while k < len(ms) and k not in trouve:
                    k += 1
                g = temps[j - 1][1] if j > 0 else ph["debut"]
                dr = trouve[k][1] if k < len(ms) else ph["fin"]
                temps[j:k] = repartir(ms[j:k], g, max(dr, g + 0.12 * (k - j)))
                j = k
        for m, (d, f) in zip(ms, temps):
            mots.append({"m": m, "d": round(d, 3), "f": round(f, 3), "k": norme(m) in MOTS_CLES, "p": i})

    ev = {}
    for nom, (p, cle) in EVTS.items():
        cand = [w for w in mots if w["p"] == p and norme(w["m"]) == cle]
        ev[nom] = cand[0]["d"] if cand else phrases[p]["debut"]
    ev["b2"] = round(ev["b1"] + 0.55, 3)
    p8 = phrases[8]
    ev["dementis"] = [round(p8["debut"] + 0.3 + k * (p8["fin"] - p8["debut"]) / 6, 3) for k in range(6)]
    p11 = phrases[11]
    ev["flashs"] = [round(p11["debut"] + x, 3) for x in (0.2, 0.7, 1.1, 1.9, 2.6, 3.4)]
    ev["frappes"] = [round(ev["ils"] + k * 0.05, 3) for k in range(len("« Ils ont agi sur ordre. »"))]

    sorties.mkdir(parents=True, exist_ok=True)
    (sorties / "phrases-enquete.json").write_text(json.dumps(phrases, ensure_ascii=False, indent=1))
    (sorties / "mots-enquete.json").write_text(json.dumps(mots, ensure_ascii=False))
    (sorties / "evts-enquete.json").write_text(json.dumps(ev, ensure_ascii=False, indent=1))
    total = sum(len(p.split()) for p in morceaux)
    print(f"{len(phrases)} phrases, {total} mots" + (f", {cales} calés par Whisper" if mots_whisper else " (estimation)"))


if __name__ == "__main__":
    main()
