# -*- coding: utf-8 -*-
"""
EuroDreams - AUDIT 2/4 : recalcul du bilan des 61 tirages,
                          fenetres glissantes, IC 95 % du TRJ, tests de derive.
"""
import numpy as np, pandas as pd
from scipy import stats

MISE = 11.50
DATA = """
2025-09-05 7.0 | 2025-09-09 0   | 2025-09-12 2.0  | 2025-09-16 2.5
2025-09-19 4.0 | 2025-09-23 4.5 | 2025-09-26 0    | 2025-09-30 5.0
2025-10-03 0   | 2025-10-07 0   | 2025-10-10 2.5  | 2025-10-14 4.5
2025-10-17 2.5 | 2025-10-21 0   | 2025-11-07 2.5  | 2025-11-11 2.5
2025-11-14 2.5 | 2025-11-18 1.5 | 2025-11-21 2.5  | 2025-11-25 0
2025-11-28 0   | 2025-12-02 6.5 | 2025-12-05 7.3  | 2025-12-09 11.7
2025-12-12 7.0 | 2025-12-16 1.5 | 2025-12-19 4.0  | 2025-12-30 0
2026-01-02 4.5 | 2026-01-06 7.5 | 2026-01-09 2.5  | 2026-01-13 2.0
2026-01-16 0   | 2026-01-20 0   | 2026-01-27 2.5  | 2026-01-30 2.5
2026-02-03 9.0 | 2026-02-06 2.5 | 2026-02-10 0    | 2026-02-13 0
2026-02-17 0   | 2026-04-27 4.0 | 2026-04-28 7.5  | 2026-05-01 0
2026-05-05 0   | 2026-05-08 5.5 | 2026-05-12 2.5  | 2026-05-15 2.5
2026-05-22 2.5 | 2026-05-26 0   | 2026-05-29 10.4 | 2026-06-02 2.5
2026-06-05 5.0 | 2026-06-09 38.5| 2026-06-12 2.5  | 2026-06-16 20.0
2026-06-19 2.5 | 2026-06-23 2.0 | 2026-06-26 0    | 2026-06-30 2.0
2026-07-03 5.0
"""
recs = []
for bloc in DATA.replace("|", "\n").split("\n"):
    bloc = bloc.strip()
    if not bloc:
        continue
    d, g = bloc.split()
    recs.append((pd.Timestamp(d), float(g)))
df = pd.DataFrame(recs, columns=["date", "gain"]).sort_values("date").reset_index(drop=True)
df["mise"] = MISE
df["net"] = df.gain - df.mise
df["cum_mise"] = df.mise.cumsum()
df["cum_gain"] = df.gain.cumsum()
df["solde"] = df.net.cumsum()

n = len(df)
print(f"n tirages          : {n}")
print(f"Total mise         : {df.mise.sum():.2f} EUR")
print(f"Total gains        : {df.gain.sum():.2f} EUR")
print(f"Solde              : {df.net.sum():.2f} EUR")
print(f"TRJ observe        : {df.gain.sum()/df.mise.sum():.4%}")
print(f"Gain moyen/tirage  : {df.gain.mean():.4f} EUR   (ecart-type {df.gain.std(ddof=1):.4f})")
print(f"Mediane des gains  : {df.gain.median():.2f} EUR")
print(f"Tirages a 0        : {(df.gain==0).sum()} ({(df.gain==0).mean():.1%})")
print(f"Tirages > mise     : {(df.gain>MISE).sum()} ({(df.gain>MISE).mean():.1%})  "
      f"-> {sorted(df.loc[df.gain>MISE,'gain'].tolist())}")
print(f"Solde max atteint  : {df.solde.max():.2f} EUR (au tirage n{df.solde.idxmax()+1})")
print(f"Solde jamais > 0   : {(df.solde>0).sum()==0}")
print(f"Duree couverte     : {df.date.min().date()} -> {df.date.max().date()} "
      f"({(df.date.max()-df.date.min()).days} jours)")

# --- fenetres terminales -------------------------------------------------
print("\n--- TRJ sur les k derniers tirages (fenetre TERMINALE) ---")
for k in (8, 28, 47, 61):
    sub = df.tail(k)
    print(f"  {k:>3} derniers : TRJ = {sub.gain.sum()/sub.mise.sum():7.2%}  "
          f"(gains {sub.gain.sum():7.2f} / mise {sub.mise.sum():7.2f})")

# le meme calcul sur les k PREMIERS, pour montrer que la 'decroissance' est un artefact
print("\n--- TRJ sur les k PREMIERS tirages (meme methode, sens inverse) ---")
for k in (8, 28, 47, 61):
    sub = df.head(k)
    print(f"  {k:>3} premiers : TRJ = {sub.gain.sum()/sub.mise.sum():7.2%}")

# --- retrait des plus gros gains ----------------------------------------
srt = df.sort_values("gain", ascending=False)
for m in (1, 2, 3):
    keep = df.drop(srt.index[:m])
    trj_a = keep.gain.sum() / df.mise.sum()            # on retire le gain, pas la mise
    trj_b = keep.gain.sum() / keep.mise.sum()          # on retire le tirage entier
    print(f"\nSans les {m} plus gros gains {srt.gain.head(m).tolist()} :"
          f"\n   TRJ (gain retire, mise conservee) = {trj_a:.2%}"
          f"\n   TRJ (tirage entier retire)        = {trj_b:.2%}")

# --- IC 95 % du TRJ ------------------------------------------------------
rng = np.random.default_rng(20260908)
g = df.gain.to_numpy()
B = 200_000
boot = rng.choice(g, size=(B, n), replace=True).mean(axis=1) / MISE
lo, hi = np.percentile(boot, [2.5, 97.5])
print("\n--- IC 95 % du TRJ, n = 61 ---")
print(f"  Bootstrap percentile      : [{lo:.2%} ; {hi:.2%}]  largeur {100*(hi-lo):.1f} pts")
se = g.std(ddof=1) / np.sqrt(n) / MISE
t = stats.t.ppf(0.975, n - 1)
print(f"  Normal / t (peu fiable)   : [{g.mean()/MISE - t*se:.2%} ; {g.mean()/MISE + t*se:.2%}]"
      f"   (SE = {se:.2%})")
# BCa-lite : bootstrap basique (pivot)
theta = g.mean() / MISE
print(f"  Bootstrap basique (pivot) : [{2*theta-hi:.2%} ; {2*theta-lo:.2%}]")
for cible, lbl in [(0.266, "mediane simulee 26,6 %"), (0.4318, "esperance modele 43,2 %"),
                   (0.52, "TRJ annonce 52 %")]:
    dedans = lo <= cible <= hi
    print(f"  {lbl:<28} dans l'IC ? {'OUI' if dedans else 'NON'}   "
          f"(p bootstrap bilateral ~ {2*min((boot<=cible).mean(),(boot>=cible).mean()):.3f})")

# --- coefficient de variation / n necessaire ----------------------------
cv = g.std(ddof=1) / g.mean()
for larg in (0.10, 0.05, 0.02):
    n_req = (2 * 1.96 * cv / (larg / (g.mean()/MISE) * (g.mean()/MISE)))**2
    n_req = (2*1.96*g.std(ddof=1)/(larg*MISE))**2
    print(f"\nPour un IC 95 % de largeur {larg:.0%} pt de TRJ il faudrait n ~ {n_req:,.0f} tirages"
          .replace(",", " "))

# --- la serie derive-t-elle ? -------------------------------------------
print("\n--- Y a-t-il une tendance temporelle dans les gains ? ---")
idx = np.arange(n)
rho, p_sp = stats.spearmanr(idx, g)
print(f"  Spearman(rang temporel, gain) : rho = {rho:+.3f}, p = {p_sp:.3f}")
h1, h2 = g[:n//2], g[n//2:]
u, p_mw = stats.mannwhitneyu(h1, h2, alternative="two-sided")
print(f"  Mann-Whitney 1re vs 2e moitie : p = {p_mw:.3f} "
      f"(moyennes {h1.mean():.2f} vs {h2.mean():.2f})")
# test des sequences sur gain>0
b = (g > 0).astype(int)
runs = 1 + (np.diff(b) != 0).sum()
n1, n0 = b.sum(), (1-b).sum()
mu = 2*n1*n0/(n1+n0) + 1
sd = np.sqrt(2*n1*n0*(2*n1*n0-n1-n0)/((n1+n0)**2*(n1+n0-1)))
print(f"  Test des sequences (gain>0)   : runs = {runs}, attendu {mu:.1f} +/- {sd:.1f}, "
      f"z = {(runs-mu)/sd:+.2f}, p = {2*(1-stats.norm.cdf(abs((runs-mu)/sd))):.3f}")

df.to_csv("out/bilan_61_tirages.csv", index=False)
print("\n-> out/bilan_61_tirages.csv ecrit")
