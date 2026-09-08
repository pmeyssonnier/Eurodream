# -*- coding: utf-8 -*-
"""
EuroDreams / Joker+ - AUDIT 7 : le TRJ REEL du Joker+, mesure sur 16 ans de
donnees financieres officielles (2011-2026, ~5 000 tirages).
Ferme le seul trou de l'audit initial.
"""
import glob, numpy as np, pandas as pd
pd.set_option("display.width", 220)

MISE_GRILLE = 1.50
def num(s):
    """'2.000,00' -> 2000.0 ; '759462,00' -> 759462.0"""
    return float(str(s).strip().replace(".", "").replace(",", "."))

frames = []
for f in sorted(glob.glob("data/jokerplus_FR_*.csv")):
    d = pd.read_csv(f, sep=";", encoding="utf-8-sig", dtype=str).dropna(how="all")
    d.columns = [c.strip().lstrip("﻿") for c in d.columns]
    d = d[d["Date"].notna() & d["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]
    for c in d.columns[1:]:
        d[c] = d[c].map(num)
    d["Date"] = pd.to_datetime(d["Date"])
    frames.append(d)
df = pd.concat(frames).sort_values("Date").reset_index(drop=True)
RANGS = list(range(1, 9))

# --- controle d'integrite : la mise est-elle bien de 1,50 EUR/grille ? ------
df["grilles"] = df.Cash / MISE_GRILLE
ent = np.isclose(df.grilles, df.grilles.round())
print("="*80)
print("0. CONTROLE D'INTEGRITE DES DONNEES")
print("="*80)
print(f"  {len(df)} tirages, du {df.Date.min().date()} au {df.Date.max().date()}")
print(f"  Cash divisible par 1,50 EUR : {ent.sum()}/{len(df)} lignes "
      f"({ent.mean():.2%}) -> la mise unitaire est bien 1,50 EUR, stable sur 16 ans")
df["grilles"] = df.grilles.round().astype(np.int64)
print(f"  Grilles/joueur : moyenne {(df.grilles/df.Joueurs).mean():.3f} "
      f"(min {(df.grilles/df.Joueurs).min():.2f}, max {(df.grilles/df.Joueurs).max():.2f})")
print(f"  Total mise      : {df.Cash.sum()/1e6:,.1f} M EUR".replace(",", " "))
print(f"  Total grilles   : {df.grilles.sum()/1e6:,.1f} M grilles".replace(",", " "))
print("\n  Montants des lots (valeurs distinctes observees) :")
for r in RANGS:
    v = np.unique(df[f"W-R{r}"])
    v = v[v > 0]
    if r == 1:
        print(f"    R1 : VARIABLE — {len(v)} valeurs, de {v.min():,.0f} a {v.max():,.0f} EUR"
              .replace(",", " ") + "   <-- SEUL rang progressif")
    else:
        print(f"    R{r} : {' / '.join(f'{x:,.2f}'.replace(',',' ') for x in v)} EUR  (FIXE)")

# --- TRJ global et par annee ------------------------------------------------
for r in RANGS:
    df[f"pay{r}"] = df[f"P-R{r}"] * df[f"W-R{r}"]
df["payout"] = df[[f"pay{r}" for r in RANGS]].sum(axis=1)
df["annee"] = df.Date.dt.year

print("\n" + "="*80)
print("1. TRJ DU JOKER+ — mesure directe (payout / mise)")
print("="*80)
TRJ = df.payout.sum() / df.Cash.sum()
TRJ_hors1 = (df.payout.sum() - df.pay1.sum()) / df.Cash.sum()
print(f"  TRJ GLOBAL 2011-2026            : {TRJ:.4%}")
print(f"  TRJ HORS jackpot (rangs 2 a 8)  : {TRJ_hors1:.4%}   <-- part quasi deterministe")
print(f"  TRJ HORS rangs 1 et 2           : "
      f"{(df.payout.sum()-df.pay1.sum()-df.pay2.sum())/df.Cash.sum():.4%}")
an = df.groupby("annee").apply(
        lambda g: pd.Series({"tirages": len(g), "mise_MEUR": g.Cash.sum()/1e6,
                             "TRJ": g.payout.sum()/g.Cash.sum(),
                             "TRJ_hors_R1": (g.payout.sum()-g.pay1.sum())/g.Cash.sum(),
                             "gagnants_R1": int(g["P-R1"].sum())}), include_groups=False)
print("\n  Par annee :")
print(an.to_string(formatters={"mise_MEUR":"{:.1f}".format, "TRJ":"{:.2%}".format,
                               "TRJ_hors_R1":"{:.2%}".format, "tirages":"{:.0f}".format}))
print(f"\n  TRJ hors R1 : moyenne {an.TRJ_hors_R1.mean():.2%}, ecart-type "
      f"{an.TRJ_hors_R1.std():.3%}  -> EXTREMEMENT stable annee apres annee.")

print("\n  Decomposition de l'esperance (sur toute la periode) :")
tot = df.payout.sum()
for r in RANGS:
    p = df[f"P-R{r}"].sum()/df.grilles.sum()
    print(f"    R{r} : p = {p:.3e} (1 sur {1/p if p>0 else float('inf'):>12,.0f}) | "
          f"lots verses {df[f'pay{r}'].sum()/1e6:8.2f} M EUR = {df[f'pay{r}'].sum()/tot:6.2%} "
          f"des gains | {df[f'pay{r}'].sum()/df.Cash.sum():6.2%} de la mise".replace(",", " "))
p_win = sum(df[f"P-R{r}"].sum() for r in RANGS)/df.grilles.sum()
print(f"\n  P(gain sur une grille Joker+) = {p_win:.4%}  (1 sur {1/p_win:.2f})")
print(f"  -> a comparer a mon estimateur par les zeros du script 05 : 25,9 % [0 % ; 54 %]")

# --- structure du jeu deduite des frequences -------------------------------
print("\n" + "="*80)
print("2. STRUCTURE DU JEU, DEDUITE DES FREQUENCES (aucun reglement consulte)")
print("="*80)
ps = {r: df[f"P-R{r}"].sum()/df.grilles.sum() for r in RANGS}
print("  Rapport de probabilite entre rangs consecutifs :")
for r in range(2, 8):
    print(f"    p(R{r+1})/p(R{r}) = {ps[r+1]/ps[r]:7.2f}")
print("  -> facteur ~10 entre rangs 3 a 7 : le jeu se gagne par nombre de CHIFFRES")
print("     correctement alignes (1 chiffre de plus = 10 fois moins probable).")
print(f"  p(R7) = {ps[7]:.4f} ~ 2 x 0,09 : compatible avec un alignement possible")
print(f"     par les DEUX extremites du numero (0,18) et non une seule (0,09).")
print(f"  p(R1) = {ps[1]:.3e} -> 1 sur {1/ps[1]:,.0f}".replace(",", " "))
print(f"     (6 chiffres x 12 signes = 1 sur 12 000 000 : p attendue {1/12e6:.3e})")

# --- le jackpot roule ------------------------------------------------------
print("\n" + "="*80)
print("3. LE JACKPOT JOKER+ ROULE — le levier qui n'existe pas en EuroDreams")
print("="*80)
old = df[df.annee <= 2016].copy()          # format ou W-R1 affiche la cagnotte courante
print(f"  Sur 2011-2016 la colonne W-R1 affiche la cagnotte EN COURS "
      f"({(old['W-R1']>0).mean():.0%} des lignes) :")
print(f"    cagnotte min {old['W-R1'][old['W-R1']>0].min():,.0f} EUR | "
      f"max {old['W-R1'].max():,.0f} EUR".replace(",", " "))
wins = df[df["P-R1"] > 0]
print(f"\n  {len(wins)} jackpots touches en 16 ans ({len(wins)/16:.1f}/an), "
      f"montants (par gagnant) :")
print(f"    min {wins['W-R1'].min():,.0f} | median {wins['W-R1'].median():,.0f} | "
      f"max {wins['W-R1'].max():,.0f} EUR".replace(",", " "))
print(f"    tirages a 2 gagnants ou plus : {(wins['P-R1']>1).sum()} "
      f"-> le rang 1 EST partage")
print(f"\n  Esperance apportee par le rang 1 selon la cagnotte (p = {ps[1]:.3e}) :")
for J in (200_000, 500_000, 1_000_000, 2_000_000, 3_125_000):
    print(f"    cagnotte {J:>9,.0f} EUR -> +{ps[1]*J:.4f} EUR/grille = "
          f"+{ps[1]*J/MISE_GRILLE:6.2%} de TRJ  => TRJ total ~ "
          f"{TRJ_hors1 + ps[1]*J/MISE_GRILLE:.2%}".replace(",", " "))
seuil = (MISE_GRILLE - TRJ_hors1*MISE_GRILLE)/ps[1]
print(f"\n  Cagnotte requise pour une esperance NON NEGATIVE : {seuil:,.0f} EUR"
      .replace(",", " "))
print(f"  Maximum jamais observe : {df['W-R1'].max():,.0f} EUR "
      f"({df['W-R1'].max()/seuil:.0%} du seuil)".replace(",", " "))

# --- comparaison EuroDreams / Joker+ ---------------------------------------
print("\n" + "="*80)
print("4. JOKER+ CONTRE EURODREAMS, par euro mise")
print("="*80)
ED, ED_H = 0.4318, 0.2818
print(f"  {'':<34}{'TRJ moyen':>12}{'TRJ hors jackpot':>20}{'P(gain)/grille':>17}")
print(f"  {'EuroDreams (2,50 EUR/grille)':<34}{ED:>11.2%}{ED_H:>19.2%}{0.214658:>16.2%}")
print(f"  {'Joker+ (1,50 EUR/grille)':<34}{TRJ:>11.2%}{TRJ_hors1:>19.2%}{p_win:>16.2%}")
print(f"\n  -> Le Joker+ redistribue {100*(TRJ-ED):+.1f} pt de plus qu'EuroDreams en moyenne,")
print(f"     et {100*(TRJ_hors1-ED_H):+.1f} pt de plus hors jackpot. Ce n'est pas marginal :")
print(f"     hors jackpot, le Joker+ rend {TRJ_hors1/ED_H:.2f} fois plus par euro.")

# --- portefeuille du joueur, recalcule -------------------------------------
print("\n" + "="*80)
print("5. LE PORTEFEUILLE DU JOUEUR, RECALCULE AVEC LE VRAI TRJ JOKER+")
print("="*80)
n, EV_ED_G, EV_ED_G_H = 61, 1.0796, 0.7044
obs = 231.90
jk_att   = n*MISE_GRILLE*TRJ
jk_att_h = n*MISE_GRILLE*TRJ_hors1
print(f"  Gains Joker+ ATTENDUS sur 61 tirages : {jk_att:.2f} EUR "
      f"({jk_att_h:.2f} hors jackpot)")
print(f"  Gains EuroDreams attendus (4 grilles): {n*4*EV_ED_G:.2f} EUR "
      f"({n*4*EV_ED_G_H:.2f} hors jackpot)")
print(f"  Total attendu hors jackpot           : {jk_att_h + n*4*EV_ED_G_H:.2f} EUR")
print(f"  Total OBSERVE                        : {obs:.2f} EUR")
print(f"  -> ratio observe/attendu (hors jackpot) = "
      f"{obs/(jk_att_h + n*4*EV_ED_G_H):.3f}")
print(f"\n  Part EuroDreams par difference : {obs - jk_att_h:.2f} EUR "
      f"sur 610 EUR mises -> TRJ_ED ~ {(obs-jk_att_h)/(n*4*2.5):.2%}")
print(f"  (borne combinatoire du script 05 : TRJ_ED <= 31,97 % — coherent)")
print(f"\n  TRJ de portefeuille ATTENDU hors jackpot : "
      f"{(jk_att_h + n*4*EV_ED_G_H)/(n*11.5):.2%}  vs  {obs/(n*11.5):.2%} observe")

print("\n" + "="*80)
print("6. BUDGET : la bonne allocation d'un euro")
print("="*80)
tir_an = 74.0
print(f"  {'strategie':<40}{'mise':>7}{'budget/an':>11}{'perte esperee/an':>18}{'perte hors jackpot':>21}")
for lbl, k, jk in (("4 grilles ED + Joker+  (actuel)", 4, 1),
                   ("4 grilles ED, sans Joker+", 4, 0),
                   ("1 grille ED + Joker+", 1, 1),
                   ("1 grille ED, sans Joker+  (reco C)", 1, 0),
                   ("Joker+ SEUL (1 grille)", 0, 1),
                   ("Joker+ SEUL x2", 0, 2)):
    m = 2.5*k + 1.5*jk
    ev  = k*EV_ED_G   + jk*MISE_GRILLE*TRJ
    evh = k*EV_ED_G_H + jk*MISE_GRILLE*TRJ_hors1
    print(f"  {lbl:<40}{m:>6.2f} {m*tir_an:>10.0f} {(m-ev)*tir_an:>17.0f} {(m-evh)*tir_an:>20.0f}")

df[["Date","annee","Joueurs","Cash","grilles","payout"]+[f"P-R{r}" for r in RANGS]] \
  .to_csv("out/jokerplus_consolide.csv", index=False)
an.to_csv("out/jokerplus_trj_par_annee.csv")
print("\n-> out/jokerplus_consolide.csv + out/jokerplus_trj_par_annee.csv")
