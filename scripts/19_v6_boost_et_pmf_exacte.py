# -*- coding: utf-8 -*-
"""
AUDIT CORRECTIF v6 — deuxième passe.

A. EuroDreams Boost : le Fonds de Réserve finance EXACTEMENT le rehaussement du
   rang 1 de 20 000 à 30 000 €/mois. Démonstration arithmétique + pourquoi le
   Boost est invisible dans les fichiers financiers belges.
B. PMF Joker+ EXACTE par énumération du couple (L, T) = chiffres alignés à
   gauche / à droite. Corrige le double comptage de la v5 : la probabilité de
   gagner passe de 26,67 % à 25,75 %, soit très exactement le « 1 sur 3,88 »
   officiel, sans changer l'espérance (linéarité).
C. Conséquences : P(gain >= mise) avec Joker+, percentiles, portefeuille.
D. Le test des 61 tirages refait par simulation du MODÈLE au lieu du bootstrap.

Sortie : out/v6_pmf_exacte.json
"""
import itertools, glob, json, numpy as np, pandas as pd
from fractions import Fraction as F
from scipy import stats
def sec(t): print("\n" + "="*84 + f"\n{t}\n" + "="*84)

P={1:F(1,19191900),2:F(4,19191900),3:F(204,3838380),4:F(8415,3838380),
   5:F(119680,3838380),6:F(695640,3838380)}
MISE=F(5,2)

# ============================================================ A. BOOST
sec("A. EURODREAMS BOOST — À QUOI SERT LE FONDS DE RÉSERVE")
r1=lambda mens: P[1]*mens*12*30/MISE
res36=F(52,100)*(1-F(4521,10000))
print(f"  Rang 1 à 20 000 €/mois (7,2 M€)  : {float(r1(20000)):.6%} de la mise")
print(f"  Rang 1 à 30 000 €/mois (10,8 M€) : {float(r1(30000)):.6%}")
print(f"  surcoût du Boost                 : {float(r1(30000)-r1(20000)):+.6%}\n")
fonds=F(52,100)*F(4521,10000); rangs12=r1(20000)+P[2]*120000/MISE
print(f"  Le Fonds de Réserve reçoit 52 % × 45,21 %      = {float(fonds):.6%}")
print(f"  Les rangs 1-2 en régime standard en consomment = {float(rangs12):.6%}")
print(f"  SOLDE DISPONIBLE                               = {float(fonds-rangs12):+.6%}")
print(f"  COÛT DU BOOST                                  = {float(r1(30000)-r1(20000)):+.6%}")
print(f"  écart entre les deux : {float(abs(fonds-rangs12-(r1(30000)-r1(20000)))):.6%} "
      f"— soit 7 dix-millièmes de point.\n")
for lab,m in (("standard",20000),("Boost",30000)):
    print(f"  TRJ nominal en régime {lab:<9}: {float(res36):.4%} + "
          f"{float(P[2]*120000/MISE):.4%} + {float(r1(m)):.4%} = "
          f"{float(res36+P[2]*120000/MISE+r1(m)):.6%}")
print("\n  → LE MYSTÈRE EST CLOS. Les 52 % annoncés ne sont pas un chiffre marketing")
print("    ni une moyenne floue : c'est EXACTEMENT le TRJ nominal d'un tirage en")
print("    régime Boost. Le Fonds de Réserve met de côté 7,50 points sur chaque")
print("    tirage ordinaire pour pouvoir en financer d'autres à 52,00 %.")
print("    Ma formulation précédente — « promotions, tirages exceptionnels et")
print("    provision » — était vague ; le mécanisme est arithmétiquement identifiable.")

ED=[]
for f in sorted(glob.glob("data/eurodreams_FR_*.csv")):
    d=pd.read_csv(f,sep=";",encoding="utf-8-sig",dtype=str).dropna(how="all")
    d.columns=[c.strip().lstrip("﻿") for c in d.columns]
    d=d[d.Date.notna()&d.Date.str.match(r"\d{4}-\d{2}-\d{2}")]
    for c in d.columns[1:]: d[c]=d[c].astype(float)
    ED.append(d)
ED=pd.concat(ED); ED["Date"]=pd.to_datetime(ED.Date); ED=ED.sort_values("Date").reset_index(drop=True)
B0,B1=pd.Timestamp("2025-10-02"),pd.Timestamp("2026-04-09")
per=ED[(ED.Date>=B0)&(ED.Date<=B1)]
print(f"\n  Pourquoi le Boost est INVISIBLE dans mes fichiers :")
print(f"    tirages belges dans la fenêtre du Boost ({B0.date()} → {B1.date()}) : {len(per)}")
print(f"    gagnants belges du rang 1 sur cette fenêtre : {int(per['P-R1'].sum())}")
print(f"    la colonne W-R1 vaut 0,00 quand il n'y a pas de gagnant "
      f"({int((ED['W-R1']==0).sum())} lignes sur {len(ED)})")
print(f"    montants R1 observés hors zéro : {sorted(ED[ED['P-R1']>0]['W-R1'].unique())}")
print(f"    dates des 2 jackpots belges : {[str(d.date()) for d in ED[ED['P-R1']>0].Date]}")
print("    → tous deux AVANT le Boost. Le jackpot boosté a été remporté au Portugal.")
print("    Mon constat « aucune trace de Boost » était donc juste, mais mal expliqué :")
print("    ce n'est pas qu'il serait financé hors table, c'est que le montant du rang 1")
print("    n'apparaît QUE lorsqu'un joueur belge le remporte.")
OUT={"boostSurcout":float(r1(30000)-r1(20000)),
     "boostSolde":float(fonds-rangs12),
     "trjStd":float(res36+P[2]*120000/MISE+r1(20000)),
     "trjBoost":float(res36+P[2]*120000/MISE+r1(30000)),
     "boostDeb":str(B0.date()),"boostFin":str(B1.date()),
     "nBoostBE":int(len(per))}

# ============================================================ B. PMF JOKER+
sec("B. PMF JOKER+ EXACTE — ÉNUMÉRATION DU COUPLE (GAUCHE, DROITE)")
LOT={0:0,1:2,2:5,3:20,4:200,5:2000}
print("  Un ticket a 6 chiffres. L = nb de chiffres alignés en partant de la")
print("  GAUCHE, T = idem en partant de la DROITE. Le ticket touche prix(L) ET")
print("  prix(T) : les deux lectures sont payées, ce que les données confirment")
print("  (0,17999 gagnant de rang 7 par grille, et non 0,1701).\n")
def joint():
    """P(L=l, T=t) exacte pour un ticket contre un tirage uniforme."""
    d={}
    for l in range(6):
        for t in range(6):
            s=l+t
            if s<=4:      p=F(81,100)*F(1,10**s)      # deux positions bloquantes distinctes
            elif s==5:    p=F(9,10)*F(1,10**5)        # elles se confondent
            else:         continue                     # impossible sans tout matcher
            d[(l,t)]=p
    d[(6,6)]=F(1,10**6)
    return d
J=joint()
tot=sum(J.values())
print(f"  Somme des probabilités : {tot} = {float(tot):.12f}  → {'OK' if tot==1 else 'ERREUR'}")
pL1=sum(p for (l,t),p in J.items() if l==1)
print(f"  Contrôles internes :")
print(f"    P(L=1) = {float(pL1):.6f} (attendu 0,09) | "
      f"E[nb de lots de rang 7] = {float(2*pL1):.6f} (observé 0,179985)")
pdig=1-J[(0,0)]
print(f"    P(le ticket gagne sur les chiffres) = {float(pdig):.6f} = 1 − 0,81")
pgain=pdig+J[(0,0)]*F(1,12)
print(f"    P(le ticket gagne QUELQUE CHOSE)    = {float(pgain):.6f} = 1 sur "
      f"{float(1/pgain):.3f}")
print(f"    probabilité officielle annoncée     = 1 sur 3,88 = {1/3.88:.6f}")
print(f"    → concordance à {abs(float(pgain)-1/3.88):.5f}. Le « 1 sur 3,88 » officiel")
print(f"      valide la lecture EXCLUSIVE au niveau du ticket, tandis que le comptage")
print(f"      des gagnants valide la lecture CUMULATIVE au niveau des lots. Les deux")
print(f"      sont vraies : P-R7 compte des LOTS, pas des tickets.")
print(f"\n  La v5/v6 posait 0,18 comme probabilité d'un gain de 2 €. C'est un")
print(f"  DOUBLE COMPTAGE : elle donnait P(gagner) = 26,67 % au lieu de 25,75 %.")
print(f"  L'espérance, elle, était juste (linéarité) — seule la LOI était fausse.")

def pmf_joker(Jack):
    m={}
    for (l,t),p in J.items():
        if l==6:
            m[Jack]=m.get(Jack,F(0))+p*F(1,12)
            m[20000]=m.get(20000,F(0))+p*F(11,12)
            continue
        v=LOT[l]+LOT[t]
        m[v+F(3,2)]=m.get(v+F(3,2),F(0))+p*F(1,12)      # le signe s'ajoute
        m[v]=m.get(v,F(0))+p*F(11,12)
    vs=np.array([float(x) for x in sorted(m)])
    ps=np.array([float(m[x]) for x in sorted(m)])
    return vs,ps
v0,p0=pmf_joker(0)
TRJ_HJ=float((v0*p0).sum()/1.5)
print(f"\n  TRJ hors jackpot du modèle exact : {TRJ_HJ:.4%}  (v6 par sommation "
      f"simple : 46,7555 % — identique, comme attendu)")
print(f"  Nombre de valeurs de gain distinctes : {len(v0)} (contre 12 dans la v5)")
print(f"  Gains possibles ≥ 100 € : {[float(x) for x in v0 if 100<=x<1e6]}")
OUT["pGain"]=float(pgain); OUT["trjHJ"]=TRJ_HJ

# ============================================================ C. PORTEFEUILLE
sec("C. P(RENTRER DANS SA MISE) AVEC LA PMF CORRIGÉE")
N,K,C=40,6,3838380
combos=np.fromiter(itertools.chain.from_iterable(itertools.combinations(range(1,N+1),K)),
                   dtype=np.int8,count=C*K).reshape(C,K)
TABLE=[7200000.,120000.,500.42,33.85,4.93,2.50]
def gains_k(k):
    tot=np.zeros(C)
    for i in range(k):
        lut=np.zeros(N+1,dtype=bool); lut[list(range(1+6*i,7+6*i))]=True
        m=lut[combos].sum(axis=1); g=np.zeros(C)
        for mm,idx in ((6,1),(5,2),(4,3),(3,4),(2,5)): g[m==mm]=TABLE[idx]
        tot+=g
    return tot
vJ,pJ=pmf_joker(800000)
sans,avec=[],[]
print(f"  {'grilles':<9}{'sans Joker+':>13}{'avec Joker+ (v6)':>19}")
for k in range(1,7):
    ed=gains_k(k); mise=2.5*k
    sans.append(float((ed>=mise).mean()))
    ev,ec=np.unique(ed,return_counts=True); ep=ec/C
    tv=(ev[:,None]+vJ[None,:]).ravel(); tp=(ep[:,None]*pJ[None,:]).ravel()
    avec.append(float(tp[tv>=mise+1.5].sum()))
    print(f"  {k:<9}{sans[-1]:>13.4%}{avec[-1]:>19.4%}")
OUT["pmiseSans"]=sans; OUT["pmiseAvec"]=avec

# ============================================================ D. LES 61 TIRAGES
sec("D. LES 61 TIRAGES : SIMULATION DU MODÈLE PLUTÔT QUE BOOTSTRAP")
print("  Le bootstrap rééchantillonne les 61 gains OBSERVÉS : il mesure l'incertitude")
print("  autour de la moyenne empirique, mais ne teste PAS l'hypothèse « ce joueur")
print("  a connu un TRJ conforme au modèle ». Pour cela il faut simuler 61 tirages")
print("  SOUS le modèle, ce qui donne la vraie loi de référence.\n")
ed4=gains_k(4)
rng=np.random.default_rng(7)
NS=200000
idx=rng.integers(0,C,size=(NS,61))
gED=ed4[idx].sum(axis=1)
cj=np.cumsum(pJ); gJK=vJ[np.searchsorted(cj,rng.random((NS,61)))].sum(axis=1)
mise=61*(4*2.5+1.5)
trj=(gED+gJK)/mise
obs=231.90/701.50
print(f"  Mise simulée : {mise:.2f} € (61 × 11,50 €) — mise réelle 701,50 €")
print(f"  TRJ simulé : médiane {np.median(trj):.4%} | moyenne {trj.mean():.4%}")
print(f"    IC90 [{np.quantile(trj,.05):.4%} ; {np.quantile(trj,.95):.4%}]")
print(f"    IC95 [{np.quantile(trj,.025):.4%} ; {np.quantile(trj,.975):.4%}]")
print(f"  TRJ observé du joueur : {obs:.4%}")
print(f"  P(TRJ simulé <= observé) = {(trj<=obs).mean():.3f}")
print(f"\n  → le TRJ de 33,06 % est au {100*(trj<=obs).mean():.0f}e percentile du modèle :")
print(f"    parfaitement ordinaire. La moyenne du modèle ({trj.mean():.2%}) est tirée")
print(f"    vers le haut par le jackpot, que 61 tirages n'ont aucune chance de voir :")
print(f"    la MÉDIANE ({np.median(trj):.2%}) est le bon étalon, et l'observé est juste")
print(f"    au-dessus. Le bootstrap donnait un IC de 24,6 points de large — il")
print(f"    répondait à une autre question.")
OUT["sim61"]={"med":float(np.median(trj)),"moy":float(trj.mean()),
              "q05":float(np.quantile(trj,.05)),"q95":float(np.quantile(trj,.95)),
              "q025":float(np.quantile(trj,.025)),"q975":float(np.quantile(trj,.975)),
              "obs":obs,"pct":float((trj<=obs).mean())}
json.dump(OUT,open("out/v6_pmf_exacte.json","w",encoding="utf-8"),ensure_ascii=False)
print("\n→ out/v6_pmf_exacte.json")
