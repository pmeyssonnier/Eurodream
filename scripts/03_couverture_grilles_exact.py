# -*- coding: utf-8 -*-
"""
EuroDreams - AUDIT 3/4 : enumeration EXHAUSTIVE des C(40,6) = 3 838 380 tirages.
Aucune simulation Monte-Carlo : toutes les probabilites ci-dessous sont exactes
(rationnelles a denominateur 3 838 380).
RAM ~ 250 Mo, duree ~ 30 s.
"""
import itertools, numpy as np, pandas as pd
from math import comb

N, K = 40, 6
C = comb(N, K)

print("Generation des", f"{C:,}".replace(",", " "), "tirages ...")
combos = np.fromiter(itertools.chain.from_iterable(itertools.combinations(range(1, N+1), K)),
                     dtype=np.int8, count=C*K).reshape(C, K)
print("ok", combos.shape, combos.nbytes/1e6, "Mo")

def matches(grille):
    lut = np.zeros(N+1, dtype=bool)
    lut[list(grille)] = True
    return lut[combos].sum(axis=1).astype(np.int8)

# --- les 4 grilles du joueur -------------------------------------------
JOUEUR = [(4,5,6,22,31,32), (5,8,16,18,19,34), (9,11,14,31,34,39), (3,16,27,29,32,37)]
DREAMS = [1, 2, 2, 3]
DISJOINT = [(1,2,3,4,5,6), (7,8,9,10,11,12), (13,14,15,16,17,18), (19,20,21,22,23,24)]

u = set().union(*map(set, JOUEUR))
print(f"\nCouverture joueur : {len(u)} numeros distincts sur 40 "
      f"({24-len(u)} doublons) -> {sorted(set(x for gl in JOUEUR for x in gl if sum(x in set(g) for g in JOUEUR)>1))}")
for i in range(4):
    for j in range(i+1, 4):
        ov = set(JOUEUR[i]) & set(JOUEUR[j])
        if ov: print(f"  G{i+1} n G{j+1} = {sorted(ov)}")
print(f"Dreams joues : {DREAMS} -> {len(set(DREAMS))} valeurs distinctes sur 5")

M_J = np.stack([matches(g) for g in JOUEUR])       # (4, C)
M_D = np.stack([matches(g) for g in DISJOINT])

# ----------------------------------------------------------------------
# Tables de gains testees. Le rang 6 (2 bons) est le seul montant certain.
# m=6 : moyenne sur le Dream = (1/5)*rang1 + (4/5)*rang2  (les deux depassent
#       toute mise envisageable -> sans effet sur P(rentrer dans sa mise)).
# ----------------------------------------------------------------------
R1_NOM, R2_NOM = 20000*12*30, 2000*12*5
def table(r3, r4, r5=5.0, r6=2.50, r1=R1_NOM, r2=R2_NOM):
    return np.array([0., 0., r6, r5, r4, r3, 0.2*r1 + 0.8*r2])

TABLES = {
    "joueur   (R3=500, R4=30)": table(500, 30),
    "observee (R3=500, R4=20)": table(500, 20),
    "basse    (R3=300, R4=15)": table(300, 15),
    "haute    (R3=900, R4=50)": table(900, 50),
    "FDJ-like (R3=250, R4=20, R5=4)": table(250, 20, 4.0),
    "R5=10    (R3=500, R4=20, R5=10)": table(500, 20, 10.0),
}

def analyse(M, tbl, mise_grille=2.50, joker=0.0, label=""):
    """M : (k, C) matrice des nb de bons numeros. Renvoie un dict de probas exactes."""
    k = M.shape[0]
    pay = tbl[M].sum(axis=0)                     # gain total du tirage, par tirage
    mise = k*mise_grille + joker
    return dict(
        label=label, k=k, mise=mise,
        p_au_moins_1_gain = float((pay > 0).mean()),
        p_ge_4_bons       = float((M >= 4).any(axis=0).mean()),
        p_rentre_mise     = float((pay >= mise).mean()),
        p_gain_gt_mise    = float((pay >  mise).mean()),
        EV                = float(pay.mean()),
        TRJ               = float(pay.mean()/mise),
        mediane_gain      = float(np.median(pay)),
        q90               = float(np.quantile(pay, 0.90)),
    )

# ----------------------------------------------------------------------
# 1. Couverture : grilles du joueur vs 4 grilles disjointes
# ----------------------------------------------------------------------
print("\n" + "="*78)
print("1. P(au moins un gain sur le tirage) — EXACT")
print("="*78)
tbl = TABLES["observee (R3=500, R4=20)"]
a_j = analyse(M_J, tbl, label="4 grilles JOUEUR (19 numeros)")
a_d = analyse(M_D, tbl, label="4 grilles DISJOINTES (24 numeros)")
for a in (a_j, a_d):
    print(f"  {a['label']:<34} P(>=1 gain) = {a['p_au_moins_1_gain']:.6f} = {a['p_au_moins_1_gain']:.4%}")
print(f"  ecart = {a_d['p_au_moins_1_gain']-a_j['p_au_moins_1_gain']:+.4%} pt")
print(f"  (1 seule grille : {analyse(M_J[:1], tbl)['p_au_moins_1_gain']:.4%})")

print("\n  P(>= 4 bons numeros sur au moins une grille) :")
print(f"    joueur     = {a_j['p_ge_4_bons']:.6%}")
print(f"    disjointes = {a_d['p_ge_4_bons']:.6%}")
p4p = (comb(6,4)*comb(34,2) + comb(6,5)*comb(34,1) + 1)/C
print(f"    borne 'lineaire' 4 x P(>=4, 1 grille) = 4 x {p4p:.6%} = {4*p4p:.6%}")
print(f"    -> la sur-additivite est de {4*p4p - a_j['p_ge_4_bons']:.2e} (chevauchements)")

print("\n  P(>=1 gain) selon le nombre de grilles (grilles du joueur, dans l'ordre) :")
for k in range(1, 5):
    print(f"    {k} grille(s) : {analyse(M_J[:k], tbl)['p_au_moins_1_gain']:.4%}")

# ----------------------------------------------------------------------
# 2. Le point 9 : P(rentrer dans sa mise) decroit-il vraiment ?
# ----------------------------------------------------------------------
print("\n" + "="*78)
print("2. P(recuperer au moins sa mise sur UN tirage) — robustesse a la table de gains")
print("="*78)
for joker, lbl in ((0.0, "SANS Joker+ (mise = 2,50 x k)"), (1.50, "AVEC Joker+ (mise = 2,50 x k + 1,50)")):
    print(f"\n  --- {lbl} ---")
    hdr = f"  {'table de gains':<32}" + "".join(f"{k} gr.".rjust(10) for k in range(1, 5))
    print(hdr); print("  " + "-"*(len(hdr)-2))
    for name, t in TABLES.items():
        row = [analyse(M_J[:k], t, joker=joker)['p_rentre_mise'] for k in range(1, 5)]
        print(f"  {name:<32}" + "".join(f"{v:9.2%} " for v in row))
    row = [analyse(M_D[:k], tbl, joker=joker)['p_rentre_mise'] for k in range(1, 5)]
    print(f"  {'observee / grilles DISJOINTES':<32}" + "".join(f"{v:9.2%} " for v in row))

print("\n  Pourquoi : seuils a franchir (table observee, sans Joker+)")
for k in range(1, 5):
    print(f"    k={k} : mise {2.5*k:5.2f} EUR ; il faut >= {int(np.ceil(2.5*k/2.5))} gains rang 6, "
          f"ou 1 rang 5 + {max(0,int(np.ceil((2.5*k-5)/2.5)))} rang 6, ou 1 rang 4 seul")

# ----------------------------------------------------------------------
# 3. Distribution exacte du rendement, mediane vs moyenne
# ----------------------------------------------------------------------
print("\n" + "="*78)
print("3. Rendement : moyenne vs mediane (table observee)")
print("="*78)
pay1 = tbl[M_J[0]]
vals, cnt = np.unique(pay1, return_counts=True)
print("  Loi exacte du gain d'UNE grille de 2,50 EUR :")
for v, c in zip(vals, cnt):
    print(f"    gain {v:>12,.2f} EUR : {c:>9,} / {C:,}  = {c/C:.8f}".replace(",", " "))
print(f"  E[gain]   = {pay1.mean():.4f} EUR -> TRJ moyen  = {pay1.mean()/2.5:.2%}")
print(f"  Mediane   = {np.median(pay1):.2f} EUR -> TRJ median = {np.median(pay1)/2.5:.2%}")
print(f"  P(gain=0) = {(pay1==0).mean():.4%}")
print("  -> la mediane du gain d'UN tirage est 0 : le 'TRJ median' n'a de sens")
print("     que cumule sur un grand nombre de tirages (cf. section 4).")

# TRJ median sur 61 tirages : simulation a partir de la loi EXACTE
print("\n  TRJ cumule sur 61 tirages, loi exacte, 4 grilles joueur + Joker+ ignore :")
rng = np.random.default_rng(7)
payJ = tbl[M_J].sum(axis=0)
draws = rng.choice(payJ, size=(200_000, 61), replace=True)
trj = draws.sum(axis=1) / (61*10.0)
print(f"    moyenne = {trj.mean():.2%} | mediane = {np.median(trj):.2%} | "
      f"IC90 = [{np.quantile(trj,.05):.2%} ; {np.quantile(trj,.95):.2%}]")
print(f"    P(TRJ observe <= 33,06 %) = {(trj <= 0.3306).mean():.3f}")
print(f"    P(solde jamais positif sur 61 tirages) : voir script 02 (chemin observe)")

res = pd.DataFrame([a_j, a_d])
res.to_csv("out/couverture_exacte.csv", index=False)
print("\n-> out/couverture_exacte.csv ecrit")
