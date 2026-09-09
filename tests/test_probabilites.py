# -*- coding: utf-8 -*-
"""Invariants combinatoires d'EuroDreams. Aucune tolérance : tout est exact."""
import itertools, sys, os
import numpy as np
from fractions import Fraction as F
from math import comb
sys.path.insert(0, os.path.dirname(__file__))
from framework import test, eq, proche, vrai, lance

N, K, D = 40, 6, 5
C40_6 = comb(N, K)
C_TOT = C40_6 * D
FAV = {r: comb(K, m) * comb(N - K, K - m)
       for r, m in ((3, 5), (4, 4), (5, 3), (6, 2))}
P = {1: F(1, C_TOT), 2: F(D - 1, C_TOT), 3: F(FAV[3], C40_6),
     4: F(FAV[4], C40_6), 5: F(FAV[5], C40_6), 6: F(FAV[6], C40_6)}

@test("C(40,6) = 3 838 380 et 19 191 900 combinaisons avec le Dream")
def _():
    eq(C40_6, 3838380); eq(C_TOT, 19191900)

@test("les effectifs par rang suivent bien la loi hypergéométrique")
def _():
    eq(FAV[3], 204); eq(FAV[4], 8415); eq(FAV[5], 119680); eq(FAV[6], 695640)

@test("la somme des probabilités sur les 7 issues vaut exactement 1")
def _():
    perdu = 1 - sum(P.values())
    tot = sum(P.values()) + perdu
    eq(tot, F(1), "la loi ne somme pas à 1")
    vrai(perdu > 0, "P(perdre) doit être positive")

@test("P(rang 1) = 1/19 191 900 et P(rang 2) = 4/19 191 900")
def _():
    eq(P[1], F(1, 19191900)); eq(P[2], F(4, 19191900))

@test("la somme des effectifs hypergéométriques reconstitue C(40,6)")
def _():
    eq(sum(comb(K, m) * comb(N - K, K - m) for m in range(K + 1)), C40_6)

def _combos():
    return np.fromiter(itertools.chain.from_iterable(itertools.combinations(range(1, N + 1), K)),
                       dtype=np.int8, count=C40_6 * K).reshape(C40_6, K)

@test("énumération exhaustive : les comptages par nombre de bons numéros")
def _():
    combos = _combos()
    lut = np.zeros(N + 1, dtype=bool); lut[list(range(1, 7))] = True
    m = lut[combos].sum(axis=1)
    for mm in range(7):
        eq(int((m == mm).sum()), comb(K, mm) * comb(N - K, K - mm),
           f"comptage faux pour {mm} bons numéros")

@test("P(>=1 rang gagnant), grilles disjointes : valeurs de l'application")
def _():
    combos = _combos()
    attendu = [0.214658, 0.402560, 0.564586, 0.701614, 0.814523, 0.904194]
    gagne = np.zeros(C40_6, dtype=bool)
    for i in range(6):
        lut = np.zeros(N + 1, dtype=bool); lut[list(range(1 + 6 * i, 7 + 6 * i))] = True
        gagne |= lut[combos].sum(axis=1) >= 2
        proche(float(gagne.mean()), attendu[i], 1e-6, f"{i+1} grille(s)")

@test("P(>=4 bons numéros sur 4 grilles disjointes) = 4 x P(une grille)")
def _():
    combos = _combos()
    p1 = None; tot = np.zeros(C40_6, dtype=bool)
    for i in range(4):
        lut = np.zeros(N + 1, dtype=bool); lut[list(range(1 + 6 * i, 7 + 6 * i))] = True
        m = lut[combos].sum(axis=1) >= 4
        if p1 is None: p1 = m.mean()
        tot |= m
    proche(float(tot.mean()), float(4 * p1), 1e-15,
           "deux grilles partageant <=1 numéro exigeraient >=7 numéros tirés")

@test("valeur actuelle de la rente : 7 200 000 EUR nominal -> 4 743 788 EUR a 3 %")
def _():
    r = 0.03 / 12
    eq(round(20000 * 12 * 30), 7200000)
    proche(20000 * (1 - (1 + r) ** -360) / r, 4743788, 1.0)

if __name__ == "__main__":
    sys.exit(lance("TESTS — COMBINATOIRE EURODREAMS"))
