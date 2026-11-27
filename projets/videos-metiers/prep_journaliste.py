#!/usr/bin/env python3
"""Cale chaque mot du texte sur la voix (Whisper, horodatage par mot) et calcule les moments clés.

Usage : python3 prep_journaliste.py texte-journaliste.txt phrases.json voix.wav DOSSIER_SORTIE
Écrit phrases-journaliste.json, mots-journaliste.json, evts-journaliste.json (lus par src/Journaliste.tsx).
"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

# mots surlignés en jaune dans les sous-titres
MOTS_CLES = {"journalisme", "jamais", "changer", "piges", "payee", "trente-cinq", "carte", "quatre", "salaire", "3560", "1951",
             "horaires", "nuits", "dimanches", "feries", "enquete", "verifier", "deux", "insultes", "mercis", "defiance",
             "six", "sources", "toujours", "ouverts", "metier", "commentaire"}

# moment clé -> (phrase, mot) ; les animations et les bruitages se calent sur le début de ce mot
EVTS = {"jamais": (1, "jamais"), "changer": (2, "changer"), "piges": (3, "piges"), "carte": (4, "carte"), "quatre": (5, "quatre"),
        "cdi": (7, "cdi"), "pigistes": (7, "pigistes"), "nuits": (9, "nuits"), "dimanches": (9, "dimanches"),
        "feries": (9, "feries"), "mois": (10, "mois"), "regle": (10, "regle"), "insultes": (11, "insultes"),
        "mercis": (11, "mercis"), "six": (12, "six"), "sources": (13, "sources"), "ouverts": (14, "ouverts")}


def norme(m):
    m = unicodedata.normalize("NFD", m.lower())
    m = "".join(ch for ch in m if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9'-]", "", m).strip("'-")


def decoupe(texte):
    return [p.strip() for p in re.findall(r"[^.?!]+[.?!]?", texte) if p.strip()]


def poids(m):
    return max(1, len(re.findall(r"[aeiouyàâéèêëîïôûù]+", m.lower())) + (6 if re.sub(r"\D", "", m).isdigit() and len(m) > 2 else 0))


def repartir(mots, d, f):
    """Répartit [d, f] entre les mots au prorata de leurs syllabes approximatives."""
    tot = sum(poids(m) for m in mots)
    t, out = d, []
    for m in mots:
        dt = (f - d) * poids(m) / tot
        out.append([t, t + dt])
        t += dt
    return out


def jetons(phrase):
    """Mots affichés : « 3 560 » reste un seul mot ; « : » et « ? » isolés se rattachent au mot d'avant."""
    ms = []
    # split(" ") et non split() : split() couperait aussi sur l'espace insécable de « 3 560 »
    for tok in [t for t in re.sub(r"(\d) (?=\d{3}\b)", "\\1\u00a0", phrase).split(" ") if t]:
        if ms and not re.search(r"\w", tok):
            ms[-1] += "\u00a0" + tok
        else:
            ms.append(tok)
    return ms


def main():
    a = sys.argv[1:]
    texte = Path(a[0]).read_text().strip()
    sorties = Path(a[-1])
    morceaux = decoupe(texte)
    phrases = json.loads(Path(a[1]).read_text())
    assert len(phrases) == len(morceaux), (len(phrases), len(morceaux))
    import librosa
    from faster_whisper import WhisperModel
    audio, _ = librosa.load(a[2], sr=16000, mono=True)
    segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(audio, language="fr", word_timestamps=True, beam_size=5)
    mots_whisper = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]

    mots, cales = [], 0
    for i, ph in enumerate(phrases):
        ms = jetons(morceaux[i])
        temps = repartir(ms, ph["debut"], ph["fin"])
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
        if not cand:
            print(f"⚠ moment « {nom} » introuvable dans la phrase {p} : début de phrase utilisé")
        ev[nom] = cand[0]["d"] if cand else phrases[p]["debut"]
    sorties.mkdir(parents=True, exist_ok=True)
    (sorties / "phrases-journaliste.json").write_text(json.dumps(phrases, ensure_ascii=False, indent=1))
    (sorties / "mots-journaliste.json").write_text(json.dumps(mots, ensure_ascii=False))
    (sorties / "evts-journaliste.json").write_text(json.dumps(ev, ensure_ascii=False, indent=1))
    total = sum(len(jetons(p)) for p in morceaux)
    print(f"{len(phrases)} phrases, {total} mots, {cales} calés par Whisper")


if __name__ == "__main__":
    main()
