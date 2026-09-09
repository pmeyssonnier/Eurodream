# -*- coding: utf-8 -*-
"""
Intégrité des fichiers officiels et faits mesurés que l'application affiche.
Ces tests échouent si un fichier de data/ change, si le parsing se casse, ou
si la Loterie modifie sa structure de gains.
"""
import glob, sys, os
import numpy as np, pandas as pd
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(__file__))
from framework import test, eq, proche, vrai, lance
RACINE = os.path.join(os.path.dirname(__file__), "..")

def charge(motif, num=True):
    """Le point est décimal dans les fichiers EuroDreams, séparateur de milliers
       dans les fichiers Joker+ : on tranche sur la présence d'une virgule."""
    out = []
    for f in sorted(glob.glob(os.path.join(RACINE, motif))):
        d = pd.read_csv(f, sep=";", encoding="utf-8-sig", dtype=str).dropna(how="all")
        d.columns = [c.strip().lstrip("﻿") for c in d.columns]
        d = d[d.Date.notna() & d.Date.str.match(r"\d{4}-\d{2}-\d{2}")]
        if num:
            for c in d.columns[1:]:
                d[c] = d[c].map(lambda s: float(str(s).strip().replace(".", "").replace(",", "."))
                                if "," in str(s) else float(str(s).strip()))
        out.append(d)
    r = pd.concat(out); r["Date"] = pd.to_datetime(r.Date)
    return r.sort_values("Date").reset_index(drop=True)

ED = charge("data/eurodreams_FR_*.csv")
JK = charge("data/jokerplus_FR_*.csv")
P = {1: 1/19191900, 2: 4/19191900, 3: 204/3838380, 4: 8415/3838380,
     5: 119680/3838380, 6: 695640/3838380}

@test("le parsing distingue bien les deux formats de nombre")
def _():
    proche(float(ED.Mise.sum()) / 1e6, 140.69, 0.01, "EuroDreams : point décimal")
    proche(float(JK.Cash.sum()) / 1e6, 963.2, 0.1, "Joker+ : virgule décimale")

@test("EuroDreams : 297 tirages, lundis et jeudis seulement")
def _():
    eq(len(ED), 297)
    eq(sorted(ED.Date.dt.dayofweek.unique()), [0, 3])
    eq(int((ED.Date.dt.dayofweek == 0).sum()), 149)

@test("EuroDreams : rang 1 toujours 7,2 M EUR, rang 2 toujours 120 000 EUR")
def _():
    eq(sorted(ED[ED["P-R1"] > 0]["W-R1"].unique()), [7200000.0])
    eq(sorted(ED[ED["P-R2"] > 0]["W-R2"].unique()), [120000.0])

@test("EuroDreams : rangs 3, 4 et 5 parimutuels, rang 6 fixe a 2,50 EUR")
def _():
    for r in (3, 4, 5):
        vrai(ED[f"W-R{r}"].nunique() > 20, f"le rang {r} devrait varier")
    eq(sorted(ED["W-R6"].unique()), [2.5])

@test("EuroDreams : la part versée aux rangs 3-6 vaut 28,44 % de la mise")
def _():
    part = sum((ED[f"P-R{r}"] * ED[f"W-R{r}"]).sum() for r in (3, 4, 5, 6)) / ED.Mise.sum()
    proche(float(part), 0.284430, 1e-5)

@test("l'identite du Fonds de Reserve : 52 % x (1 - 45,21 %) = ce qui est verse")
def _():
    part = sum((ED[f"P-R{r}"] * ED[f"W-R{r}"]).sum() for r in (3, 4, 5, 6)) / ED.Mise.sum()
    proche(float(part), 0.52 * (1 - 0.4521), 0.0006, "concordance a 0,05 point")

@test("le solde du Fonds de Reserve finance exactement un Boost")
def _():
    r1 = lambda m: F(1, 19191900) * m * 12 * 30 / F(5, 2)
    solde = F(52, 100) * F(4521, 10000) - r1(20000) - F(4, 19191900) * 120000 / F(5, 2)
    cout = r1(30000) - r1(20000)
    proche(float(solde), float(cout), 1e-5, "solde et cout du Boost doivent coincider")
    trj_boost = F(52, 100) * (1 - F(4521, 10000)) + F(4, 19191900) * 120000 / F(5, 2) + r1(30000)
    proche(float(trj_boost), 0.52, 1e-5, "en regime Boost le TRJ nominal vaut 52 %")

@test("le Boost est invisible : aucun jackpot belge dans sa fenêtre")
def _():
    f = ED[(ED.Date >= "2025-10-02") & (ED.Date <= "2026-04-09")]
    vrai(len(f) > 40, "la fenêtre doit couvrir plusieurs dizaines de tirages")
    eq(int(f["P-R1"].sum()), 0)
    eq([str(d.date()) for d in ED[ED["P-R1"] > 0].Date], ["2025-05-01", "2025-07-07"])

@test("Joker+ : 5 057 tirages et lots fixes hors rang 1")
def _():
    eq(len(JK), 5057)
    for r, v in ((2, 20000.), (3, 2000.), (4, 200.), (5, 20.), (6, 5.), (7, 2.), (8, 1.5)):
        eq(sorted(JK[f"W-R{r}"].unique()), [v], f"le rang {r} doit être fixe")

@test("Joker+ : les fréquences de gagnants collent à 2 x 0,9 x 10^-k")
def _():
    G = (JK.Cash / 1.5).round().sum()
    for r, k in ((7, 1), (6, 2), (5, 3), (4, 4), (3, 5)):
        p = 2 * 0.9 * 10 ** -k
        z = (JK[f"P-R{r}"].sum() - G * p) / np.sqrt(G * p * (1 - p))
        vrai(abs(z) < 3, f"rang {r} : z = {z:+.1f}, la structure ne colle plus")

@test("Joker+ : 57 jackpots observés, compatibles avec 1/12 000 000")
def _():
    G = (JK.Cash / 1.5).round().sum()
    eq(int(JK["P-R1"].sum()), 57)
    att = G / 12e6
    proche(att, 53.5, 1.0)
    vrai(abs(57 - att) < 2.5 * att ** 0.5, "57 doit rester dans ~2,5 sigma de 53,5")

@test("Joker+ : le lot « signe » est cumulatif (P(R8) = 1/12, pas 0,0667)")
def _():
    G = (JK.Cash / 1.5).round().sum()
    proche(float(JK["P-R8"].sum() / G), 1 / 12, 5e-5)

@test("sur-dispersion EuroDreams : les joueurs cochent (Var(z) = 54,22 au rang 6)")
def _():
    n = (ED.Mise / 2.5).round().to_numpy(float)
    z = (ED["P-R6"].to_numpy(float) - n * P[6]) / np.sqrt(n * P[6] * (1 - P[6]))
    proche(float(z.var()), 54.22, 0.05)
    vrai(z.var() > 20, "sans sur-dispersion la conclusion « les joueurs cochent » tombe")

if __name__ == "__main__":
    sys.exit(lance("TESTS — DONNÉES OFFICIELLES"))
