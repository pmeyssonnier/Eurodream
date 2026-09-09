# -*- coding: utf-8 -*-
"""
Loi du gain d'une grille Joker+, dérivée des règles et non ajustée.
Les tests vérifient à la fois la cohérence interne (la loi somme à 1) et
l'accord avec les DEUX faits observables, qui semblaient s'opposer :
  · 0,179985 lot de rang 7 par grille (642 M de grilles)   -> lecture cumulative
  · 1 chance sur 3,88 de gagner (chiffre officiel)          -> lecture exclusive
"""
import sys, os
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(__file__))
from framework import test, eq, proche, vrai, lance

LOT = {0: 0, 1: 2, 2: 5, 3: 20, 4: 200, 5: 2000}
LOT_R2, LOT_SIGNE = 20000, F(3, 2)
MISE = F(3, 2)

def joint():
    """P(L=l, T=t) : chiffres alignés à gauche / à droite, exact."""
    d = {}
    for l in range(6):
        for t in range(6):
            s = l + t
            if s <= 4:   d[(l, t)] = F(81, 100) * F(1, 10 ** s)
            elif s == 5: d[(l, t)] = F(9, 10) * F(1, 10 ** 5)
    d[(6, 6)] = F(1, 10 ** 6)
    return d
J = joint()

def pmf(jackpot):
    m = {}
    for (l, t), p in J.items():
        if l == 6:
            m[F(jackpot)] = m.get(F(jackpot), F(0)) + p * F(1, 12)
            m[F(LOT_R2)] = m.get(F(LOT_R2), F(0)) + p * F(11, 12)
            continue
        v = F(LOT[l] + LOT[t])
        m[v + LOT_SIGNE] = m.get(v + LOT_SIGNE, F(0)) + p * F(1, 12)
        m[v] = m.get(v, F(0)) + p * F(11, 12)
    return m

@test("la loi jointe (L, T) somme exactement à 1")
def _():
    eq(sum(J.values()), F(1))

@test("aucun couple (L, T) impossible n'est inclus")
def _():
    for (l, t) in J:
        vrai(l + t <= 5 or (l == 6 and t == 6),
             f"le couple ({l}, {t}) ne peut pas exister sans que tout corresponde")

@test("P(L = 1) = 0,09 et E[nb de lots de rang 7] = 0,18")
def _():
    pL1 = sum(p for (l, t), p in J.items() if l == 1)
    eq(pL1, F(9, 100))
    eq(2 * pL1, F(18, 100), "c'est ce que compte P-R7 : des LOTS, pas des tickets")

@test("E[nb de lots] par rang = 2 x 0,9 x 10^-k, comme observé sur 642 M de grilles")
def _():
    obs = {1: 1.799850e-01, 2: 1.799358e-02, 3: 1.801065e-03,
           4: 1.798646e-04, 5: 1.805779e-05}
    for k, o in obs.items():
        att = float(2 * sum(p for (l, t), p in J.items() if l == k))
        proche(att, 2 * 0.9 * 10 ** -k, 1e-15, f"k = {k}")   # tolérance flottante
        proche(att, o, 4 * o ** 0.5 * (642.1e6) ** -0.5 + 1e-9,
               f"k = {k} : le modèle s'écarte de l'observé")

@test("P(le ticket gagne quelque chose) = 25,75 % = 1 sur 3,88 officiel")
def _():
    pdig = 1 - J[(0, 0)]
    eq(pdig, F(19, 100), "P(au moins un chiffre) doit valoir 1 - 0,81")
    pg = pdig + J[(0, 0)] * F(1, 12)
    eq(pg, F(103, 400))
    proche(float(1 / pg), 3.88, 0.005, "le « 1 sur 3,88 » officiel")

@test("P(rang 1) = 1/12 000 000 et P(rang 2) = 11/12 000 000")
def _():
    m = pmf(999999)
    eq(J[(6, 6)] * F(1, 12), F(1, 12000000))
    eq(J[(6, 6)] * F(11, 12), F(11, 12000000))
    proche(float(1 / (J[(6, 6)] * F(11, 12))), 1090909, 1)

@test("la PMF somme à 1 pour n'importe quelle cagnotte")
def _():
    for jk in (0, 200000, 800000, 3125000):
        eq(sum(pmf(jk).values()), F(1), f"cagnotte {jk}")

@test("TRJ hors jackpot = 46,7555 % — 0,05 pt de l'observé (46,8010 % sur 963 M EUR)")
def _():
    m = pmf(0)
    ev = sum(v * p for v, p in m.items())
    proche(float(ev / MISE), 0.4675554722, 1e-9)
    proche(float(ev / MISE), 0.4680098818, 0.0005, "écart au versé réel")

@test("pente de la cagnotte = 5,5556 points de TRJ par million")
def _():
    proche(float(F(1, 12000000) * 1000000 / MISE), 0.0555555, 1e-6)

@test("seuil d'espérance nulle = 9 584 002 EUR")
def _():
    m = pmf(0); ev = sum(v * p for v, p in m.items())
    seuil = (1 - float(ev / MISE)) * 1.5 / (1 / 12000000)
    proche(seuil, 9584002, 2)

@test("le double comptage de la v5 est bien détecté (26,67 % au lieu de 25,75 %)")
def _():
    faux = 0.18 + 0.018 + 0.0018 + 0.00018 + 0.000018 + 1e-6
    faux += (1 - faux) / 12
    proche(faux, 0.266667, 1e-5)
    vrai(abs(faux - 0.2575) > 0.008, "l'erreur doit être visible")

if __name__ == "__main__":
    sys.exit(lance("TESTS — LOI DU GAIN JOKER+"))
