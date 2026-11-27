#!/usr/bin/env python3
"""Mixe la voix off avec une nappe sombre et des bruitages, tous synthétisés ici (aucun fichier externe, aucun droit).

Usage : python3 mix_enquete.py voix.wav evts-enquete.json phrases-enquete.json sortie.wav
Les bruitages tombent aux mêmes instants que les animations (mêmes moments clés que la vidéo).
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
N = int((ph[-1]["fin"] + 1.6) * sr)
v = np.pad(v, (0, max(0, N - len(v))))[:N]
rng = np.random.default_rng(7)
T = np.arange(N) / sr


def filtre(x, f, type_):
    return sosfilt(butter(2, f, type_, fs=sr, output="sos"), x)


def bruit(n):
    return rng.standard_normal(n)


def env(n, attaque, decl):
    t = np.arange(n) / sr
    return np.minimum(1, t / max(attaque, 1e-4)) * np.exp(-t / decl)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


# ─── Sons ────────────────────────────────────────────────────────────────────
def explosion():
    n = int(2.6 * sr); t = np.arange(n) / sr
    f = 28 + 40 * np.exp(-t / 0.15)
    sub = np.sin(2 * np.pi * np.cumsum(f) / sr) * env(n, 0.003, 0.7)
    souffle = filtre(bruit(n), 900, "low") * env(n, 0.002, 0.35)
    crepit = filtre(bruit(n), 2500, "high") * env(n, 0.001, 0.06)
    return norm(sub + 0.8 * norm(souffle) + 0.25 * norm(crepit))


def impact():
    n = int(1.8 * sr); t = np.arange(n) / sr
    sub = np.sin(2 * np.pi * np.cumsum(45 + 50 * np.exp(-t / 0.08)) / sr) * env(n, 0.002, 0.5)
    return norm(sub + 0.4 * norm(filtre(bruit(n), 600, "low") * env(n, 0.001, 0.12)))


def tampon():
    n = int(0.35 * sr); t = np.arange(n) / sr
    choc = np.sin(2 * np.pi * 130 * t) * env(n, 0.001, 0.05)
    clac = filtre(bruit(n), 1800, "high") * env(n, 0.0005, 0.012)
    return norm(choc + 0.6 * norm(clac))


def souffle():
    n = int(0.5 * sr); t = np.arange(n) / sr
    x = sosfilt(butter(2, [400, 3500], "band", fs=sr, output="sos"), bruit(n))
    return norm(x * np.sin(np.pi * t / t[-1]) ** 2)


def tic():
    n = int(0.05 * sr); t = np.arange(n) / sr
    return norm(np.sin(2 * np.pi * 2200 * t) * env(n, 0.0003, 0.004))


def frappe():
    n = int(0.06 * sr)
    return norm(filtre(bruit(n), 1500, "high") * env(n, 0.0003, 0.007) + 0.5 * np.sin(2 * np.pi * 320 * np.arange(n) / sr) * env(n, 0.0005, 0.01))


def flash():
    n = int(0.25 * sr); t = np.arange(n) / sr
    return norm(filtre(bruit(n), 3000, "high") * env(n, 0.0005, 0.015) + 0.3 * np.sin(2 * np.pi * (3000 + 4000 * t) * t) * env(n, 0.01, 0.08))


def ping():
    n = int(1.5 * sr); t = np.arange(n) / sr
    return norm(np.sin(2 * np.pi * 880 * t) * env(n, 0.002, 0.4) + 0.3 * np.sin(2 * np.pi * 1320 * t) * env(n, 0.002, 0.25))


def pop():
    n = int(0.12 * sr); t = np.arange(n) / sr
    return norm(np.sin(2 * np.pi * np.cumsum(500 + 3000 * t) / sr) * env(n, 0.002, 0.04))


def montee(d=1.0):
    n = int(d * sr); t = np.arange(n) / sr
    x = sosfilt(butter(2, [300, 6000], "band", fs=sr, output="sos"), bruit(n))
    return norm(x * (t / d) ** 2.5)


# ─── Placement ───────────────────────────────────────────────────────────────
fx = np.zeros(N)


def poser(son, t, db):
    i = int(t * sr)
    if 0 <= i < N:
        k = min(len(son), N - i)
        fx[i:i + k] += son[:k] * 10 ** (db / 20)


F = 1 / 30  # une image
CHOC = 5 * F  # un tampon touche le papier 5 images après son apparition
poser(impact(), 0.0, -5)
for i in (3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14):  # débuts de scènes
    poser(souffle(), ph[i]["debut"] - 0.4, -21)
for k in range(int((ph[2]["debut"] - ph[1]["debut"]) / 0.5)):
    poser(tic(), ph[1]["debut"] + k * 0.5, -24)
poser(explosion(), ev["b1"], -2)
poser(explosion(), ev["b2"], -3)
poser(ping(), ev["mururoa"] + 0.3, -20)
poser(tampon(), ev["faux"] + CHOC, -9)
poser(tampon(), ev["faux"] + 7 * F + CHOC, -10)
poser(tampon(), ev["agents"] + CHOC, -9)
for s in ev["dementis"]:
    poser(tampon(), s + CHOC, -12)
poser(tampon(), ev["demission"] + CHOC, -8)
for s in ev["flashs"]:
    poser(flash(), s, -19)
for s in ev["frappes"]:
    poser(frappe(), s, -23)
poser(impact(), ev["qui"], -6)
poser(montee(1.0), ev["vingt"] - 0.2, -22)
poser(impact(), ev["partie2"], -7)
poser(pop(), ev["abonne"], -15)

# ─── Nappe : bourdon grave + souffle + pouls qui accélère vers la fin ─────────
nappe = (0.5 * np.sin(2 * np.pi * 55 * T) + 0.35 * np.sin(2 * np.pi * 82.41 * T + 0.3 * np.sin(2 * np.pi * 0.07 * T))
         + 0.15 * np.sin(2 * np.pi * 110.4 * T)) * (0.65 + 0.35 * np.sin(2 * np.pi * T / 9))
nappe += 0.35 * norm(filtre(bruit(N), 350, "low")) * (0.6 + 0.4 * np.sin(2 * np.pi * T / 13))
coeur = np.zeros(N)
t, debut_pouls = ph[5]["debut"], ph[5]["debut"]
while t < ph[-1]["fin"]:
    n = int(0.3 * sr); tt = np.arange(n) / sr
    b = np.sin(2 * np.pi * 52 * tt) * env(n, 0.004, 0.08)
    for dt, g in ((0, 1.0), (0.22, 0.6)):
        i = int((t + dt) * sr)
        k = min(n, N - i)
        if k > 0:
            coeur[i:i + k] += b[:k] * g
    t += 1.15 - 0.35 * min(1, (t - debut_pouls) / (ph[12]["debut"] - debut_pouls))
nappe += 0.9 * coeur
nappe *= np.clip(T / 0.8, 0, 1) * np.clip((N / sr - T) / 2.0, 0, 1)
meter = pyln.Meter(sr)
nappe *= 10 ** ((-31 - meter.integrated_loudness(nappe)) / 20)
# la nappe baisse sous la voix (−4 dB) et remonte dans les silences
activite = uniform_filter1d((np.abs(v) > 0.02).astype(float), int(0.3 * sr))
nappe *= 1 - 0.37 * np.clip(activite * 3, 0, 1)

# ─── Mixage final : −14 LUFS, crêtes −1 dBFS ─────────────────────────────────
# la vidéo joue ce mono sur deux canaux (+3 dB) : on mesure la version stéréo
volume = lambda x: meter.integrated_loudness(np.stack([x, x], axis=1))
y = v + nappe + fx
lim, fen = 10 ** (-1 / 20), int(sr * 0.005)
for _ in range(6):
    y = y * 10 ** ((-14 - volume(y)) / 20)
    g = np.minimum(1.0, lim / np.maximum(np.abs(y), 1e-9))
    y = y * uniform_filter1d(minimum_filter1d(g, 2 * fen + 1), 2 * fen + 1)
    if abs(volume(y) + 14) < 0.3 and np.max(np.abs(y)) <= lim * 1.01:
        break
y = np.clip(y, -lim, lim)
sf.write(sortie, y.astype(np.float32), sr)
print(f"{sortie} : {N / sr:.1f} s, {volume(y):.1f} LUFS, crête {20 * np.log10(np.max(np.abs(y))):.1f} dBFS")
