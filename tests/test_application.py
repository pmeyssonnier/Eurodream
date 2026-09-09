# -*- coding: utf-8 -*-
"""
L'application et les scripts doivent dire la même chose.

Ces tests attrapent exactement la classe de bug qui a coûté le plus cher dans ce
projet : une constante recopiée à la main dans le HTML et oubliée quand le calcul
change. Le dernier test va plus loin — il exécute la fonction JavaScript
setJackpot() dans node et compare la loi qu'elle produit à la loi exacte.
"""
import json, os, re, subprocess, sys, tempfile
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(__file__))
from framework import test, eq, proche, vrai, lance
from test_joker_pmf import pmf, J as JOINT

RACINE = os.path.join(os.path.dirname(__file__), "..")
APP = os.path.join(RACINE, "eurodreams_v6.html")
HTML = open(APP, encoding="utf-8").read()

SANS_COM = re.sub(r"/\*.*?\*/", "", HTML, flags=re.S)

def const(nom):
    """Une déclaration peut être groupée : const A = ..., B = ..., C = ...;"""
    m = re.search(rf"\b{nom} = ([^;,\n]+)[;,\n]", SANS_COM)
    vrai(m is not None, f"constante {nom} introuvable dans l'application")
    return eval(m.group(1).strip())

def tableau(nom):
    m = re.search(rf"const {nom} = \[([^\]]*)\];", HTML)
    vrai(m is not None, f"tableau {nom} introuvable")
    return [float(x) for x in m.group(1).split(",")]

CAG = json.loads(re.search(r"const CAG = (\{.*?\});\n", HTML, re.S).group(1))
POP = json.loads(re.search(r"const POP = (\{.*?\});\n", HTML, re.S).group(1))

@test("l'application déclare P(rang 1) = 1/12 000 000, pas la valeur empirique")
def _():
    proche(const("P_R1_JK"), 1 / 12000000, 1e-18)
    proche(const("P_R2_JK"), 11 / 12000000, 1e-18)
    vrai(abs(const("P_R1_JK") - 8.877052e-08) > 1e-9,
         "l'ancienne estimation empirique est de retour")

@test("TRJ hors jackpot de l'application = celui de la loi exacte")
def _():
    ev = sum(v * p for v, p in pmf(0).items())
    proche(const("TRJ_JK_HJ"), float(ev / F(3, 2)), 1e-7)

@test("seuil d'espérance nulle embarqué = celui que la loi implique")
def _():
    ev = float(sum(v * p for v, p in pmf(0).items()) / F(3, 2))
    proche(CAG["seuil"], (1 - ev) * 1.5 * 12000000, 2)

@test("les TRJ des 7 tranches de cagnotte suivent la pente exacte")
def _():
    ev = float(sum(v * p for v, p in pmf(0).items()) / F(3, 2))
    for lab, part, trj in CAG["tranches"]:
        lo, hi = [float(x) * 1e6 for x in lab.replace(" M", "").split("–")]
        proche(trj, ev + (lo + hi) / 2 / 12000000 / 1.5, 1e-5, f"tranche {lab}")

@test("PMISE_SANS et PMISE_AVEC sont cohérentes entre elles")
def _():
    sans, avec = tableau("PMISE_SANS"), tableau("PMISE_AVEC")
    eq(len(sans), 6); eq(len(avec), 6)
    proche(sans[0], 0.214658, 1e-6, "1 grille sans Joker+ = P(>=1 rang gagnant)")
    vrai(avec[0] < sans[0],
         "à 1 grille, ajouter le Joker+ relève le seuil de 2,50 à 4,00 EUR")
    for k in range(2, 6):
        vrai(avec[k] > sans[k], f"à {k+1} grilles le Joker+ doit aider")

@test("PMISE_AVEC vient de la loi EXACTE, pas de l'ancienne loi double-comptée")
def _():
    avec = tableau("PMISE_AVEC")
    proche(avec[0], 0.102083, 5e-6, "valeur de la loi exacte")
    vrai(abs(avec[0] - 0.097460) > 1e-3, "l'ancienne valeur (double comptage) est de retour")

@test("P1_EXACT correspond à l'énumération des 3 838 380 tirages")
def _():
    eq([round(x, 6) for x in tableau("P1_EXACT")],
       [0.214658, 0.402560, 0.564586, 0.701614, 0.814523, 0.904194])

@test("les données de l'onglet Popularité viennent bien du modèle de co-gagnants")
def _():
    eq(len(POP["signes"]), 12)
    for o in POP["signes"]:
        att = (1 - pow(2.718281828459045, -o["lam"])) / o["lam"]
        proche(o["e"], att, 1e-9, f"E[1/(1+K)] faux pour {o['s']}")
    vrai(POP["levier"] < 0.0002, "le levier du signe doit rester sous 0,02 point")
    vrai(abs(POP["levier"] - 0.00436) > 1e-3, "l'ancien +0,436 point est de retour")

@test("l'onglet Popularité ne revendique plus de levier sur les CHIFFRES du Joker+")
def _():
    for interdit in ("0 sous-joué", "7 sur-joué", "+0,57 point", "signature humaine"):
        vrai(interdit not in HTML, f"le texte « {interdit} » ne devrait plus exister")

@test("aucune date construite en UTC (toISOString) dans l'application")
def _():
    vrai("toISOString" not in SANS_COM,
         "toISOString enregistre la veille en Belgique entre minuit et 2 h "
         "(les commentaires sont exclus du contrôle)")

@test("le titre et le sous-titre annoncent la bonne version")
def _():
    vrai("v6" in re.search(r"<title>(.*?)</title>", HTML).group(1), "titre obsolète")
    vrai('<div class="sub">v6 ·' in HTML, "sous-titre obsolète")

@test("le générateur ne prétend plus que l'espérance est identique pour toute grille")
def _():
    vrai("quelle que soit la grille cochée" not in HTML,
         "contradiction avec les rangs parimutuels")
    vrai("même <b>probabilité de sortir</b>" in HTML or
         "probabilité de sortir</b>" in HTML, "la formulation correcte a disparu")

@test("le générateur plafonne les grilles disjointes à 6")
def _():
    vrai("strat === 'disj' ? Math.min(n, 6)" in HTML,
         "6 grilles occupent 36 numéros sur 40 : au-delà c'est impossible")

@test("EXÉCUTION RÉELLE : setJackpot() de l'application reproduit la loi exacte")
def _():
    src = re.search(r"(const JK_LOTS = .*?)\nconst P_GAIN_JK", HTML, re.S).group(1)
    src = re.sub(r"^const trjJk = .*$", "", src, flags=re.M)
    js = (src.replace("let JK_V = [], JK_P = [];", "let JK_V = [], JK_P = [];")
          + "\nsetJackpot(800000);\nconsole.log(JSON.stringify([JK_V,JK_P]));\n")
    if "let JK_V" not in js: js = "let JK_V=[],JK_P=[];\n" + js
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as f:
        f.write(js); chemin = f.name
    try:
        r = subprocess.run(["node", chemin], capture_output=True, text=True, timeout=30)
        vrai(r.returncode == 0, f"node a échoué :\n{r.stderr[:400]}")
        vals, probs = json.loads(r.stdout)
    finally:
        os.unlink(chemin)
    proche(sum(probs), 1.0, 1e-12, "la loi produite par l'application ne somme pas à 1")
    ref = pmf(800000)
    eq(len(vals), len(ref), "nombre de valeurs de gain distinctes")
    for v, p in zip(vals, probs):
        vrai(F(v).limit_denominator(2) in ref or F(v) in ref, f"gain {v} inattendu")
        proche(p, float(ref[F(v).limit_denominator(2)]), 1e-15, f"probabilité du gain {v}")
    pj = dict(zip(vals, probs))
    proche(pj[800000], const("P_R1_JK"), 1e-18,
           "la loi et la constante P_R1_JK doivent avoir la même source")
    proche(pj[20000], const("P_R2_JK"), 1e-18)
    proche(pj[0.0], 0.81 * 11 / 12, 1e-12, "P(gain nul) = 0,81 x 11/12")
    proche(1 - pj[0.0], 0.2575, 1e-9,
           "P(le ticket gagne quelque chose) doit valoir 25,75 %, pas 26,67 %")
    ev_js = sum(v * p for v, p in zip(vals, probs))
    ev_py = float(sum(v * p for v, p in ref.items()))
    proche(ev_js, ev_py, 1e-9, "espérance divergente entre JavaScript et Python")

if __name__ == "__main__":
    sys.exit(lance("TESTS — COHÉRENCE APPLICATION / SCRIPTS"))
