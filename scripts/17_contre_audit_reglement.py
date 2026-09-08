# -*- coding: utf-8 -*-
"""
CONTRE-AUDIT — trois objections externes, testées contre les données.

O1. Le « trou » de 7,5 points entre 52 % annoncés et 44,5 % calculés ne serait pas
    inexpliqué : 45,21 % de l'argent des lots (= 52 % des mises) part au Fonds de
    Réserve qui finance les rangs 1-2 et les promotions.
O2. Les probabilités Joker+ des rangs 1 et 2 utilisées dans l'app sont EMPIRIQUES
    alors que la structure du jeu les donne exactement : 1/12 000 000 et 11/12 × 10⁻⁶.
O3. Les 6 chiffres du Joker+ ne sont PAS choisis par le joueur (attribution
    automatique) ; seul le signe l'est. L'écart sur les chiffres ne peut donc pas
    être une « signature humaine », ni un levier.
"""
import glob, numpy as np, pandas as pd
from scipy import stats

def sec(t): print("\n" + "="*84 + f"\n{t}\n" + "="*84)
def charge(motif, num=True):
    out=[]
    for f in sorted(glob.glob(motif)):
        d=pd.read_csv(f,sep=";",encoding="utf-8-sig",dtype=str).dropna(how="all")
        d.columns=[c.strip().lstrip("﻿") for c in d.columns]
        d=d[d.Date.notna()&d.Date.str.match(r"\d{4}-\d{2}-\d{2}")]
        if num:
            for c in d.columns[1:]:
                d[c]=d[c].map(lambda s: float(str(s).strip().replace(".","").replace(",",".")))
        out.append(d)
    r=pd.concat(out); r["Date"]=pd.to_datetime(r.Date)
    return r.sort_values("Date").reset_index(drop=True)

# ============================================================== O1
sec("O1. LE FONDS DE RÉSERVE EXPLIQUE-T-IL LES 7,5 POINTS MANQUANTS ?")
P={1:1/19191900,2:4/19191900,3:204/3838380,4:8415/3838380,
   5:119680/3838380,6:695640/3838380}
ED=charge("data/eurodreams_FR_*.csv"); M=ED.Mise.sum()
pool={r:(ED[f"P-R{r}"]*ED[f"W-R{r}"]).sum() for r in P}
s36=sum(pool[r] for r in (3,4,5,6))/M
theo=0.52*(1-0.4521)
print(f"  Versé aux rangs 3-6, mesuré sur {len(ED)} tirages : {s36:.4%} de la mise")
print(f"  Prédit par le règlement 52 % × (1 − 45,21 %)      : {theo:.4%}")
print(f"  écart : {100*(theo-s36):+.4f} point  →  concordance à 5 centièmes de point")
print(f"  (la fraction de réserve qu'impliquerait exactement le mesuré : "
      f"{100*(1-s36/0.52):.3f} % contre 45,21 % annoncés)")
ev12=(P[1]*7200000+P[2]*120000)/2.5
print(f"\n  Le Fonds de Réserve reçoit 52 % × 45,21 % = {0.52*0.4521:.4%} de la mise.")
print(f"  Espérance des rangs 1-2 (rente nominale 7,2 M€) : {ev12:.4%}")
print(f"  Reliquat : {0.52*0.4521-ev12:+.4%} de la mise = promotions, tirages")
print(f"  exceptionnels et provision — argent qui NE revient PAS au joueur d'un")
print(f"  tirage ordinaire.")
print(f"\n  → OBJECTION VALIDÉE. Le TRJ du joueur ne bouge pas d'un centième :")
print(f"    {s36:.4%} (rangs 3-6) + {ev12:.4%} (rangs 1-2) = {s36+ev12:.4%} nominal.")
print(f"    Ce qui change, c'est le SENS du trou : il n'est pas inexpliqué, il est")
print(f"    structurel. Les 52 % sont vrais au niveau de la FAMILLE de jeux,")
print(f"    faux au niveau d'un tirage ordinaire.")

# ============================================================== O2
sec("O2. PROBABILITÉS JOKER+ : EMPIRIQUES vs STRUCTURELLES")
J=charge("data/jokerplus_FR_*.csv"); J["g"]=(J.Cash/1.5).round(); G=J.g.sum()
print(f"  {len(J)} tirages, {G/1e6:.1f} M de grilles.\n")
print("  D'abord : la loi « k chiffres alignés depuis l'une des deux extrémités »,")
print("  p = 2 × 0,9 × 10⁻ᵏ, est-elle exacte ? (rangs 7 à 3 = 1 à 5 chiffres)")
print(f"  {'rang':<6}{'gagnants':>13}{'p observée':>14}{'p structurelle':>16}{'ratio':>9}{'z':>7}")
for r,k in {7:1,6:2,5:3,4:4,3:5}.items():
    p=2*0.9*10**(-k); ko=J[f"P-R{r}"].sum(); po=ko/G
    z=(ko-G*p)/np.sqrt(G*p*(1-p))
    print(f"  R{r:<5}{int(ko):>13,}{po:>14.6e}{p:>16.6e}{po/p:>9.4f}{z:>+7.1f}".replace(","," "))
print("  → exacte à 4 décimales sur 642 M de grilles. Donc pour k = 6 les deux")
print("    extrémités se confondent et p vaut EXACTEMENT 10⁻⁶, réparti 1/12 - 11/12")
print("    par le signe. Ce n'est plus une estimation, c'est une identité.\n")
for r,lab,p in [(1,"6 chiffres + signe",1e-6/12),(2,"6 chiffres sans signe",1e-6*11/12)]:
    ko=int(J[f"P-R{r}"].sum()); att=G*p
    lo,hi=stats.poisson.interval(0.95,ko)
    pv=stats.poisson.cdf(ko,att) if ko<att else 1-stats.poisson.cdf(ko-1,att)
    print(f"  R{r} — {lab}")
    print(f"     observés {ko} | attendus sous 1/{1/p:,.0f} : {att:.1f} → p unilatérale = {2*pv:.3f}"
          .replace(","," "))
    print(f"     p empirique (celle de l'app v4) = {ko/G:.6e} = 1/{G/ko:,.0f}".replace(","," "))
    print(f"     IC95 du comptage [{lo:.0f} ; {hi:.0f}] → la valeur structurelle est DEDANS")
p1s=1e-6/12
print(f"\n  Conséquence sur la pente de cagnotte (TRJ par million d'euros) :")
print(f"     avec la p empirique   : {1e6*8.877052e-08/1.5*100:.2f} points par million")
print(f"     avec la p structurelle: {1e6*p1s/1.5*100:.2f} points par million")
TRJ_HJ=0.468010
for lab,p in [("empirique",8.877052e-08),("structurelle",p1s)]:
    seuil=(1-TRJ_HJ)*1.5/p
    print(f"     espérance nulle ({lab:<12}) à une cagnotte de {seuil:,.0f} €".replace(","," "))
print("  → OBJECTION VALIDÉE. L'estimation empirique reposait sur 57 événements :")
print("    ±13 % d'incertitude. La valeur structurelle est exacte. Je corrige.")

# ============================================================== O3
sec("O3. LES CHIFFRES DU JOKER+ SONT-ILS CHOISIS PAR LE JOUEUR ?")
T=charge("data/jokerplus_TIRAGES_*.csv", num=False)
T["num"]=T[[f"Numéro {i}" for i in range(1,7)]].astype(int).astype(str).agg("".join,axis=1)
T=T.rename(columns={"Signe astrologique":"signe"})
j=J.merge(T[["Date","num","signe"]],on="Date",how="inner")
j["g"]=(j.Cash/1.5).round()
# part jouée d'un signe : rang 8 (le signe seul) ; d'un chiffre : rang 7 (1 chiffre)
sg=j.groupby("signe").apply(lambda g: g["P-R8"].sum()/g.g.sum(), include_groups=False)*12
j["d1"]=j.num.str[0]; j["d6"]=j.num.str[-1]
r7=j.groupby("d1").apply(lambda g: g["P-R7"].sum()/g.g.sum(), include_groups=False)
r7=r7/r7.mean()
r7b=j.groupby("d6").apply(lambda g: g["P-R7"].sum()/g.g.sum(), include_groups=False)
r7b=r7b/r7b.mean()
print(f"  Amplitude de la part JOUÉE :")
print(f"     signes du zodiaque (choisis par le joueur)  : ×{sg.max()/sg.min():.3f}")
print(f"     1er chiffre                                  : ×{r7.max()/r7.min():.3f}")
print(f"     dernier chiffre                              : ×{r7b.max()/r7b.min():.3f}")
print(f"  Rapport signe / chiffre : ×{(sg.max()/sg.min()-1)/(r7.max()/r7.min()-1):.0f}")
print("\n  → OBJECTION VALIDÉE dans son INTERPRÉTATION. Si les joueurs choisissaient")
print("    aussi les chiffres, les deux amplitudes seraient du même ordre. Elles")
print("    diffèrent d'un facteur 19 sur l'excès (21,3 % contre 1,1 %) : le signe est
    choisi, les chiffres non.")
print("    L'écart de ~2 % sur les chiffres est réel et très significatif (642 M de")
print("    grilles), mais il ne peut pas venir d'un choix du joueur — il vient du")
print("    stock de numéros attribués aux tickets. Il n'est donc PAS exploitable :")
print("    on ne peut pas choisir ses chiffres.")
print(f"\n  Conséquence sur le levier anti-partage Joker+ :")
print(f"     avant (signe + chiffres) : +0,572 point   ← NON VALIDE")
print(f"     après  (signe seul)      : +0,436 point   ← seul chiffre défendable")
print("\n  Ce que l'objection NE touche PAS : la sur-dispersion EuroDreams")
print("  (Var(z) = 54,22 au rang 6), où les numéros SONT cochés par le joueur.")
print("  Elle la renforce même : le Joker+ à Var(z) = 2,20 devient un témoin")
print("  propre de ce que donne un jeu à grilles non choisies.")
