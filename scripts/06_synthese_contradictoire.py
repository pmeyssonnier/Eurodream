# -*- coding: utf-8 -*-
"""
EuroDreams - SYNTHESE : confrontation chiffre par chiffre + 2 tests cibles
  (i)  robustesse du 'point 9' : balayage fin du gain rang 5
  (ii) le bon etalon de comparaison pour un echantillon de 61 tirages
"""
import itertools, numpy as np, pandas as pd
from math import comb
pd.set_option("display.width", 200)

N, K = 40, 6; C = comb(N, K)
combos = np.fromiter(itertools.chain.from_iterable(itertools.combinations(range(1, N+1), K)),
                     dtype=np.int8, count=C*K).reshape(C, K)
def matches(g):
    lut = np.zeros(N+1, bool); lut[list(g)] = True
    return lut[combos].sum(1).astype(np.int8)
JOUEUR = [(4,5,6,22,31,32),(5,8,16,18,19,34),(9,11,14,31,34,39),(3,16,27,29,32,37)]
M = np.stack([matches(g) for g in JOUEUR])

# ---------------------------------------------------------------- (i)
print("="*78)
print("(i) POINT 9 : P(rentrer dans sa mise) decroit-elle avec le nb de grilles ?")
print("    Balayage du gain rang 5 (3 bons) ; rang 3 et rang 4 fixes a 500 / 20.")
print("="*78)
R1 = 0.2*(20000*12*30) + 0.8*(2000*12*5)
rows = []
for r5 in [2.5, 3, 4, 5, 6, 7.5, 8, 10, 12.5, 15, 20]:
    tbl = np.array([0., 0., 2.5, r5, 20., 500., R1])
    pr = []
    for k in range(1, 5):
        pay = tbl[M[:k]].sum(0)
        pr.append((pay >= 2.5*k).mean())
    rows.append(dict(rang5=r5, **{f"{k}_grille": pr[k-1] for k in range(1, 5)},
                     monotone="DECROISSANT" if pr == sorted(pr, reverse=True) else "non monotone"))
t = pd.DataFrame(rows)
print(t.to_string(index=False, formatters={c: "{:.2%}".format for c in t.columns if "grille" in c}))
print("\n  Balayage du rang 4 (rang 5 fige a 5 EUR) :")
rows = []
for r4 in [5, 10, 15, 20, 25, 30, 40, 60, 100]:
    tbl = np.array([0., 0., 2.5, 5., float(r4), 500., R1])
    pr = [ (tbl[M[:k]].sum(0) >= 2.5*k).mean() for k in range(1,5) ]
    rows.append(dict(rang4=r4, **{f"{k}_grille": pr[k-1] for k in range(1,5)}))
t4 = pd.DataFrame(rows)
print(t4.to_string(index=False, formatters={c: "{:.2%}".format for c in t4.columns if "grille" in c}))
print("\n  Balayage du rang 3 (500 -> 5000) : sans aucun effet (le rang 3 depasse")
for r3 in (250, 500, 2000, 5000):
    tbl = np.array([0., 0., 2.5, 5., 20., float(r3), R1])
    print(f"    rang3={r3:>5} : " + " ".join(f"{(tbl[M[:k]].sum(0)>=2.5*k).mean():.4%}" for k in range(1,5)))
print("  toujours la mise, quel que soit k <= 4 -> il n'entre jamais dans l'arbitrage).")

print("\n  CONCLUSION (i) : le phenomene n'est PAS un artefact du rang 3 ni du rang 4.")
print("  Il depend ENTIEREMENT du rapport rang5/rang6 a la mise unitaire :")
print("  il s'inverse des que le rang 5 vaut >= 7,50 EUR (= 3 mises unitaires).")

# ---------------------------------------------------------------- (ii)
print("\n" + "="*78)
print("(ii) QUEL ETALON pour 61 tirages ? moyenne, mediane, ou 'hors jackpot' ?")
print("="*78)
p = {1:1/19191900, 2:4/19191900, 3:204/C, 4:8415/C, 5:119680/C, 6:695640/C}
ev_tot   = p[1]*20000*12*30 + p[2]*120000 + p[3]*500 + p[4]*20 + p[5]*5 + p[6]*2.5
ev_no_r1 = ev_tot - p[1]*20000*12*30
ev_no_r12= ev_no_r1 - p[2]*120000
print(f"  TRJ moyen (avec rang 1 nominal)   : {ev_tot/2.5:.2%}")
print(f"  TRJ moyen HORS rang 1             : {ev_no_r1/2.5:.2%}   <- etalon realiste")
print(f"  TRJ moyen HORS rangs 1 et 2       : {ev_no_r12/2.5:.2%}")
print(f"  P(aucun rang 1 en 244 grilles)    : {(1-p[1])**244:.6f}")
print(f"  P(aucun rang 3+ en 244 grilles)   : {(1-p[3]-p[2]-p[1])**244:.4f}")
print("\n  -> sur 61 tirages, le rang 1 a 1 chance sur ~78 000 de se produire.")
print("     L'etalon pertinent n'est ni 43,2 % (moyenne, dominee par un evenement")
print("     quasi impossible) ni 26,6 % (une mediane simulee) mais 28,2 % :")
print("     l'esperance CONDITIONNELLE a l'absence de jackpot.")

# comparaison au reel
GAINS = np.array([7.0,0,2.0,2.5,4.0,4.5,0,5.0,0,0,2.5,4.5,2.5,0,2.5,2.5,2.5,1.5,2.5,0,
                  0,6.5,7.3,11.7,7.0,1.5,4.0,0,4.5,7.5,2.5,2.0,0,0,2.5,2.5,9.0,2.5,0,0,
                  0,4.0,7.5,0,0,5.5,2.5,2.5,2.5,0,10.4,2.5,5.0,38.5,2.5,20.0,2.5,2.0,0,2.0,5.0])
print(f"\n  Observe (portefeuille, mise 11,50) : {GAINS.sum()/(61*11.5):.2%}")
print(f"  Observe rapporte a la seule mise EuroDreams (10,00) : {GAINS.sum()/(61*10):.2%}")
print(f"  Borne sup. de la part EuroDreams / mise EuroDreams   : 31.97%")
print(f"  Etalon hors jackpot                                  : {ev_no_r1/2.5:.2%}")
print("  -> le joueur est AU-DESSUS de l'etalon realiste, pas en-dessous.")

# test formel : le TRJ observe est-il compatible avec le modele hors jackpot ?
rng = np.random.default_rng(2026)
tbl = np.array([0., 0., 2.5, 5., 20., 500., 0.])       # rang 1/2 neutralises
payJ = tbl[M].sum(0)
sim = rng.choice(payJ, size=(200_000, 61)).sum(1)/(61*10)
print(f"\n  Loi du TRJ EuroDreams sur 61 tirages (hors jackpot, 4 grilles) :")
print(f"    moyenne {sim.mean():.2%} | mediane {np.median(sim):.2%} | "
      f"IC90 [{np.quantile(sim,.05):.2%} ; {np.quantile(sim,.95):.2%}]")
print(f"    P(TRJ >= 31,97 %) = {(sim >= 0.3197).mean():.3f}   "
      f"(percentile du joueur : {(sim <= 0.3197).mean():.1%})")
