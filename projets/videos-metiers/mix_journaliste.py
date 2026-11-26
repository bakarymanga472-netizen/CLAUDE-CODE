#!/usr/bin/env python3
"""Mixe la voix off avec une musique « lo-fi anime » et des bruitages, tous synthétisés ici (aucun fichier externe, aucun droit).

Usage : python3 mix_journaliste.py voix.wav evts-journaliste.json phrases-journaliste.json sortie.wav
Musique : enchaînement IV-V-iii-vi (la progression typique des génériques d'anime), piano électrique, basse,
batterie feutrée. Elle s'assombrit (filtre, sans batterie) sur la pige et la défiance, et repart ensuite.
Les bruitages tombent aux mêmes instants que les animations de src/Journaliste.tsx.
"""
import json, sys
import numpy as np, pyloudnorm as pyln, soundfile as sf
from scipy.ndimage import minimum_filter1d, uniform_filter1d
from scipy.signal import butter, sosfilt

voix_f, evts_f, phrases_f, sortie = sys.argv[1:5]
v, sr = sf.read(voix_f, dtype="float64")
v = v.mean(axis=1) if v.ndim > 1 else v
ev = json.load(open(evts_f))
ph = json.load(open(phrases_f))
F = 1 / 30  # une image de la vidéo
N = int((ph[-1]["fin"] + 1.4) * sr)  # même durée que la composition
v = np.pad(v, (0, max(0, N - len(v))))[:N]
rng = np.random.default_rng(11)
T = np.arange(N) / sr
DUREE = N / sr


def filtre(x, f, type_, ordre=2):
    return sosfilt(butter(ordre, f, type_, fs=sr, output="sos"), x)


def bruit(n):
    return rng.standard_normal(n)


def env(n, attaque, decl):
    t = np.arange(n) / sr
    return np.minimum(1, t / max(attaque, 1e-4)) * np.exp(-t / decl)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


def poser(piste, son, t, db):
    i = int(t * sr)
    if i < 0:
        son, i = son[-i:], 0
    if i < N:
        k = min(len(son), N - i)
        piste[i:i + k] += son[:k] * 10 ** (db / 20)


def courbe(points):
    """Enveloppe linéaire par morceaux : [(temps, valeur), ...]."""
    ts, vs = zip(*points)
    return np.interp(T, ts, vs)


# ─── Musique ─────────────────────────────────────────────────────────────────
BPM = 88
TEMPS = 60 / BPM
MESURE = 4 * TEMPS
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
# Fa maj7, Sol 6, Mi m7, La m7 (notes MIDI), une mesure chacun
ACCORDS = [(53, [65, 69, 72, 76]), (55, [67, 71, 74, 76]), (52, [64, 67, 71, 74]), (57, [64, 69, 72, 76])]


def piano(f, d, vel=1.0):
    n = int(d * sr); t = np.arange(n) / sr
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.35)
         + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.12))
    x *= 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)  # léger trémolo
    return vel * x * env(n, 0.006, 1.1)


def cloche(f, d=1.2, vel=1.0):
    n = int(d * sr); t = np.arange(n) / sr
    return vel * (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t / 0.15)) * env(n, 0.002, 0.45)


def basse(f, d):
    n = int(d * sr); t = np.arange(n) / sr
    return np.sin(2 * np.pi * f * t) * env(n, 0.01, 0.6) * np.clip((d - t) / 0.05, 0, 1)


def kick():
    n = int(0.35 * sr); t = np.arange(n) / sr
    return np.sin(2 * np.pi * np.cumsum(45 + 75 * np.exp(-t / 0.04)) / sr) * env(n, 0.002, 0.16)


def caisse():
    n = int(0.25 * sr); t = np.arange(n) / sr
    return 0.6 * norm(filtre(bruit(n), [900, 5000], "band") * env(n, 0.001, 0.07)) + 0.4 * np.sin(2 * np.pi * 190 * t) * env(n, 0.001, 0.05)


def charleston():
    n = int(0.06 * sr)
    return norm(filtre(bruit(n), 7000, "high") * env(n, 0.0005, 0.012))


clavier, grave, batterie = np.zeros(N), np.zeros(N), np.zeros(N)
k, debut = 0, 0.0
while debut < DUREE:
    racine, notes = ACCORDS[k % 4]
    for j, m in enumerate(notes):  # accord plaqué, très légèrement égrené
        poser(clavier, piano(hz(m), MESURE + 0.6, 0.55), debut + 0.012 * j, 0)
    for c in range(8):  # arpège en croches, avec swing
        m = notes[[0, 2, 1, 3, 2, 3, 1, 2][c]] + 12
        poser(clavier, cloche(hz(m), 0.9, 0.22 if c % 2 == 0 else 0.15), debut + c * TEMPS / 2 + (0.06 if c % 2 else 0), 0)
    poser(grave, basse(hz(racine - 12), 2 * TEMPS), debut, 0)
    poser(grave, basse(hz(racine - 12), 1.5 * TEMPS), debut + 2.5 * TEMPS, -3)
    for b in range(4):
        if b in (0, 2):
            poser(batterie, kick(), debut + b * TEMPS, 0)
        else:
            poser(batterie, caisse(), debut + b * TEMPS, -5)
        poser(batterie, charleston(), debut + b * TEMPS, -16)
        poser(batterie, charleston(), debut + (b + 0.5) * TEMPS + 0.06, -20)
    poser(batterie, kick(), debut + 2.75 * TEMPS, -6)
    debut += MESURE
    k += 1

# scènes sombres : la pige (phrase 3) et la défiance (phrase 12)
def scene(p, q):
    return ph[p]["debut"] - 4 * F, ph[q + 1]["debut"] - 4 * F


p3, d12 = scene(3, 3), scene(12, 12)
sombre = courbe([(0, 0), (p3[0] - 0.3, 0), (p3[0], 1), (p3[1] - 0.2, 1), (p3[1] + 0.2, 0), (d12[0] - 0.3, 0), (d12[0], 1),
                 (d12[1] - 0.2, 1), (d12[1] + 0.2, 0), (DUREE, 0)])
# la batterie entre aux débuts (phrase 2) et sort dans les scènes sombres
gain_batt = courbe([(0, 0), (ph[2]["debut"] - 0.2, 0), (ph[2]["debut"], 1), (DUREE, 1)]) * (1 - sombre)
musique = clavier + 0.9 * grave
clair = filtre(musique, 5500, "low")
etouffe = filtre(musique, 700, "low", 4) * 1.4
musique = clair * (1 - sombre) + etouffe * sombre + 0.55 * filtre(batterie, 9000, "low") * gain_batt
musique *= np.clip(T / 0.3, 0, 1) * np.clip((DUREE - T) / 1.6, 0, 1)
meter = pyln.Meter(sr)
musique *= 10 ** ((-24 - meter.integrated_loudness(musique)) / 20)
# la musique baisse sous la voix (−6 dB) et remonte dans les silences
activite = uniform_filter1d((np.abs(v) > 0.02).astype(float), int(0.25 * sr))
musique *= 1 - 0.5 * np.clip(activite * 3, 0, 1)


# ─── Bruitages ───────────────────────────────────────────────────────────────
def impact():
    n = int(1.6 * sr); t = np.arange(n) / sr
    sub = np.sin(2 * np.pi * np.cumsum(42 + 60 * np.exp(-t / 0.07)) / sr) * env(n, 0.002, 0.45)
    return norm(sub + 0.45 * norm(filtre(bruit(n), 700, "low") * env(n, 0.001, 0.1)))


def swish():
    n = int(0.4 * sr); t = np.arange(n) / sr
    x = filtre(bruit(n), [800, 6000], "band")
    return norm(x * np.sin(np.pi * t / t[-1]) ** 3)


def pop(f0=500):
    n = int(0.12 * sr); t = np.arange(n) / sr
    return norm(np.sin(2 * np.pi * np.cumsum(f0 + 3200 * t) / sr) * env(n, 0.002, 0.035))


def scintille():
    s = np.zeros(int(1.4 * sr))
    for j, m in enumerate([84, 88, 91, 96, 100]):
        c = cloche(hz(m), 1.0, 0.7)
        i = int(j * 0.06 * sr)
        s[i:i + len(c)] += c[:len(s) - i]
    return norm(s)


def compteur():
    n = int(0.5 * sr); t = np.arange(n) / sr
    return norm(np.sin(2 * np.pi * 1318 * t) * env(n, 0.002, 0.12) + 0.5 * np.sin(2 * np.pi * 1975 * t) * env(n, 0.002, 0.08))


def declencheur():
    n = int(0.12 * sr)
    return norm(filtre(bruit(n), 2500, "high") * (env(n, 0.0005, 0.008) + 0.6 * np.roll(env(n, 0.0005, 0.01), int(0.045 * sr))))


def notif_douce():
    n = int(0.6 * sr); t = np.arange(n) / sr
    return norm(np.sin(2 * np.pi * 1568 * t) * env(n, 0.002, 0.15) + np.sin(2 * np.pi * 2093 * t) * env(n, 0.002, 0.15) * (t > 0.09))


def notif_seche():
    n = int(0.3 * sr); t = np.arange(n) / sr
    return norm(np.sign(np.sin(2 * np.pi * 220 * t)) * env(n, 0.001, 0.06) * 0.5 + np.sin(2 * np.pi * 180 * t) * env(n, 0.001, 0.08))


def pluie(d):
    n = int(d * sr)
    x = 0.6 * filtre(bruit(n), [1500, 8000], "band")
    gouttes = (rng.random(n) < 120 / sr).astype(float)
    x += filtre(np.convolve(gouttes * rng.uniform(0.3, 1, n), np.exp(-np.arange(int(0.004 * sr)) / (0.0008 * sr)), "same"), 1800, "high") * 6
    t = np.arange(n) / sr
    return norm(x) * np.clip(t / 0.5, 0, 1) * np.clip((d - t) / 0.5, 0, 1)


fx = np.zeros(N)
poser(fx, impact(), 0.0, -6)
poser(fx, swish(), 2 * F, -16)
poser(fx, impact(), 4 * F, -9)                       # « 10 ANS »
poser(fx, pop(), ev["jamais"] - 4 * F, -14)
for p in (2, 3, 4, 6, 8, 10, 11, 12, 13, 14, 15):   # changements de scène (flash blanc)
    poser(fx, swish(), ph[p]["debut"] - 4 * F - 0.15, -15)
poser(fx, scintille(), ev["changer"], -17)
poser(fx, pop(), ev["changer"], -15)
poser(fx, pluie(p3[1] - p3[0]), p3[0], -24)
poser(fx, pop(380), ev["piges"], -15)
for j in range(5):                                   # flashs des photographes
    poser(fx, declencheur(), ph[4]["debut"] + 0.15 + j * 0.37 + rng.uniform(0, 0.1), -19)
poser(fx, impact(), ev["carte"], -11)
poser(fx, compteur(), ev["carte"] + 0.05, -17)
poser(fx, swish(), ph[5]["debut"], -14)
poser(fx, impact(), ph[5]["debut"] + 2 * F, -10)     # « 1 SUR 4 »
poser(fx, pop(), ph[6]["debut"] - 2 * F, -13)       # « LE SALAIRE ?! »
poser(fx, impact(), ev["cdi"], -11)
poser(fx, compteur(), ev["cdi"] + 0.05, -17)
poser(fx, impact(), ev["pigistes"], -11)
poser(fx, compteur(), ev["pigistes"] + 0.05, -17)
s8 = scene(8, 9)
poser(fx, pluie(s8[1] - s8[0]), s8[0], -25)
poser(fx, pop(), ph[8]["debut"] - 2 * F, -13)       # « LES HORAIRES ?! »
for n_ in ("nuits", "dimanches", "feries"):
    poser(fx, pop(), ev[n_], -14)
poser(fx, impact(), ev["mois"], -11)
poser(fx, pop(650), ev["regle"], -14)
for j in range(5):
    poser(fx, notif_seche(), ev["insultes"] + 3 * j * F, -19)
    poser(fx, notif_douce(), ev["mercis"] + 3 * j * F, -19)
poser(fx, impact(), ev["six"], -9)
poser(fx, pop(650), ev["sources"], -14)
poser(fx, scintille(), ev["ouverts"], -16)
poser(fx, scintille(), ph[15]["debut"] - 4 * F, -16)
poser(fx, pop(), ph[15]["debut"], -13)

# ─── Mixage final : −14 LUFS, crêtes −1,5 dBFS ───────────────────────────────
# La vidéo joue le son sur deux canaux : un mono à −14 LUFS y devient −11 LUFS (+3 dB).
# On mesure donc la version stéréo, celle que TikTok recevra, et on écrit directement en stéréo.
y = v + musique + fx
stereo = lambda x: np.stack([x, x], axis=1)
volume = lambda x: meter.integrated_loudness(stereo(x))
lim, fen = 10 ** (-1.5 / 20), int(sr * 0.005)  # 0,5 dB de marge : l'encodage AAC fait dépasser les crêtes
for _ in range(6):
    y = y * 10 ** ((-14 - volume(y)) / 20)
    g = np.minimum(1.0, lim / np.maximum(np.abs(y), 1e-9))
    y = y * uniform_filter1d(minimum_filter1d(g, 2 * fen + 1), 2 * fen + 1)
    if abs(volume(y) + 14) < 0.3 and np.max(np.abs(y)) <= lim * 1.01:
        break
y = np.clip(y, -lim, lim)
sf.write(sortie, stereo(y).astype(np.float32), sr)
print(f"{sortie} : {DUREE:.1f} s, {volume(y):.1f} LUFS (stéréo), crête {20 * np.log10(np.max(np.abs(y))):.1f} dBFS")
