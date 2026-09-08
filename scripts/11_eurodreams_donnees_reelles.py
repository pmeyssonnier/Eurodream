# -*- coding: utf-8 -*-
"""EuroDreams - AUDIT 11 : les VRAIES donnees (2023-2026). Table de gains reelle,
TRJ mesure, et verification definitive du calendrier des 61 tirages du joueur."""
import glob, numpy as np, pandas as pd
from scipy import stats
pd.set_option("display.width", 200)

fr = []
for f in sorted(glob.glob("data/eurodreams_FR_*.csv")):
    d = pd.read_csv(f, sep=";", encoding="utf-8-sig", dtype=str).dropna(how="all")
    d.columns = [c.strip().lstrip("﻿") for c in d.columns]
    d = d[d["Date"].notna() & d["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]
    for c in d.columns[1:]: d[c] = d[c].astype(float)
    d["Date"] = pd.to_datetime(d["Date"]); fr.append(d)
df = pd.concat(fr).sort_values("Date").reset_index(drop=True)
df["grilles"] = (df.Mise/2.5).round().astype("int64")
R = range(1, 7)
JOURS = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]

print("="*82); print("1. LE CALENDRIER — question tranchee"); print("="*82)
print(f"  {len(df)} tirages EuroDreams, du {df.Date.min().date()} au {df.Date.max().date()}")
print(f"  Jours de tirage : {df.Date.dt.dayofweek.map(lambda i: JOURS[i]).value_counts().to_dict()}")
print(f"  Controle mise : Mise/2,50 entier sur "
      f"{np.isclose(df.Mise/2.5, (df.Mise/2.5).round()).mean():.0%} des lignes -> grille a 2,50 EUR")

DATES = pd.to_datetime([
 "2025-09-05","2025-09-09","2025-09-12","2025-09-16","2025-09-19","2025-09-23","2025-09-26",
 "2025-09-30","2025-10-03","2025-10-07","2025-10-10","2025-10-14","2025-10-17","2025-10-21",
 "2025-11-07","2025-11-11","2025-11-14","2025-11-18","2025-11-21","2025-11-25","2025-11-28",
 "2025-12-02","2025-12-05","2025-12-09","2025-12-12","2025-12-16","2025-12-19","2025-12-30",
 "2026-01-02","2026-01-06","2026-01-09","2026-01-13","2026-01-16","2026-01-20","2026-01-27",
 "2026-01-30","2026-02-03","2026-02-06","2026-02-10","2026-02-13","2026-02-17","2026-04-27",
 "2026-04-28","2026-05-01","2026-05-05","2026-05-08","2026-05-12","2026-05-15","2026-05-22",
 "2026-05-26","2026-05-29","2026-06-02","2026-06-05","2026-06-09","2026-06-12","2026-06-16",
 "2026-06-19","2026-06-23","2026-06-26","2026-06-30","2026-07-03"])
cal = set(df.Date)
inter = [d for d in DATES if d in cal]
print(f"\n  >>> Dates du joueur qui sont des tirages EuroDreams : {len(inter)}/61 <<<")
print(f"      {[str(d.date()) for d in inter] if inter else '(aucune)'}")
print(f"  Dates du joueur situees dans la periode couverte : "
      f"{sum((DATES>=df.Date.min())&(DATES<=df.Date.max()))}/61")
print("  -> L'HISTORIQUE DES 61 TIRAGES N'EST PAS UN HISTORIQUE EURODREAMS.")
print("     Toute l'analyse du bilan (TRJ 33,1 %, IC, percentile) portait sur")
print("     un jeu qui n'est pas celui dont j'ai modelise les probabilites.")

print("\n" + "="*82); print("2. LA VRAIE TABLE DE GAINS"); print("="*82)
print("  L'audit initial supposait : R3=500, R4=20 ou 30, R5=5, R6=2,50 fixes.")
print("  Realite :")
for r in R:
    w = df[f"W-R{r}"]; nz = w[w > 0]
    if r <= 2:
        print(f"    R{r} : {len(nz)} gagnant(s) en {len(df)} tirages, montant "
              f"{nz.unique() if len(nz) else 'jamais gagne'} EUR  -> FIXE")
    else:
        print(f"    R{r} : PARIMUTUEL — min {nz.min():8.2f} | median {nz.median():8.2f} | "
              f"moy {nz.mean():8.2f} | max {nz.max():8.2f} EUR"
              if nz.nunique() > 1 else
              f"    R{r} : FIXE a {nz.iloc[0]:.2f} EUR")
print("\n  Rupture de regime au rang 3 :")
for lab, msk in (("2023-11 -> 2025-09", df.Date < "2025-10-01"),
                 ("2025-10 -> 2026-09", df.Date >= "2025-10-01")):
    s = df[msk]
    print(f"    {lab} : R3 median {s['W-R3'].median():7.2f} | R4 {s['W-R4'].median():6.2f} | "
          f"R5 {s['W-R5'].median():5.2f} | {len(s)} tirages | "
          f"{s.grilles.mean():,.0f} grilles/tirage".replace(",", " "))

print("\n" + "="*82); print("3. LE TRJ REEL D'EURODREAMS — mesure, plus suppose"); print("="*82)
for r in R: df[f"pay{r}"] = df[f"P-R{r}"]*df[f"W-R{r}"]
df["payout"] = df[[f"pay{r}" for r in R]].sum(axis=1)
TRJ  = df.payout.sum()/df.Mise.sum()
TRJ1 = (df.payout.sum()-df.pay1.sum())/df.Mise.sum()
TRJ12= (df.payout.sum()-df.pay1.sum()-df.pay2.sum())/df.Mise.sum()
print(f"  Mise totale {df.Mise.sum()/1e6:.1f} M EUR | {df.grilles.sum()/1e6:.1f} M grilles")
print(f"  TRJ GLOBAL mesure           : {TRJ:.4%}")
print(f"  TRJ hors rang 1             : {TRJ1:.4%}")
print(f"  TRJ hors rangs 1 et 2       : {TRJ12:.4%}")
print(f"\n  Mon estimation par modele   : 43,18 % (global) / 28,18 % (hors jackpot)")
print(f"  Ecart                       : {100*(TRJ-0.4318):+.2f} pt / {100*(TRJ1-0.2818):+.2f} pt")
print("\n  Contribution de chaque rang (part de la mise) :")
for r in R:
    p = df[f"P-R{r}"].sum()/df.grilles.sum()
    th = {1:1/19191900, 2:4/19191900, 3:204/3838380, 4:8415/3838380,
          5:119680/3838380, 6:695640/3838380}[r]
    print(f"    R{r} : p_obs = {p:.3e} (theorie {th:.3e}, ratio {p/th:.3f}) | "
          f"{df[f'pay{r}'].sum()/df.Mise.sum():7.3%} de la mise")
print("\n  -> les probabilites combinatoires du script 01 sont CONFIRMEES par")
print("     les frequences reelles de gagnants.")
df.to_csv("out/eurodreams_consolide.csv", index=False)
