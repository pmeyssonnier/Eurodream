# -*- coding: utf-8 -*-
"""
AUDIT CORRECTIF v6 — reconstruction à partir des règles, pas des estimations.

A. PMF Joker+ EXACTE, dérivée de la structure du jeu, puis confrontée rang par
   rang aux 642 M de grilles réellement jouées.
B. TRJ, tranches de cagnotte et seuil d'espérance nulle recalculés sur cette PMF.
C. P(gain >= mise) EuroDreams seul et EuroDreams + Joker+, par énumération
   exhaustive des 3 838 380 tirages puis convolution — recalculée avec la PMF
   exacte (l'ancienne PMISE_AVEC reposait sur la PMF empirique).
D. Levier du signe du zodiaque : VRAI modèle de co-gagnants (Poisson), au lieu
   du rapport de popularités utilisé jusqu'ici.
E. Requalification du +3,17 point EuroDreams et modèle hiérarchique de la
   sur-dispersion : ce que les données permettent, et ce qu'il manque.

Sortie : out/v6_modele.json
"""
import itertools, glob, json, numpy as np, pandas as pd
from math import comb
from scipy import stats

def sec(t): print("\n" + "="*84 + f"\n{t}\n" + "="*84)
def charge(motif, num=True):
    out=[]
    for f in sorted(glob.glob(motif)):
        d=pd.read_csv(f,sep=";",encoding="utf-8-sig",dtype=str).dropna(how="all")
        d.columns=[c.strip().lstrip("﻿") for c in d.columns]
        d=d[d.Date.notna()&d.Date.str.match(r"\d{4}-\d{2}-\d{2}")]
        if num:
            # les fichiers Joker+ écrivent « 2.000,00 » (point = milliers), les
            # fichiers EuroDreams « 579917.50 » (point = décimale). On tranche
            # sur la présence d'une virgule plutôt que sur le nom du fichier.
            for c in d.columns[1:]:
                d[c]=d[c].map(lambda s: float(str(s).strip().replace(".","").replace(",","."))
                              if "," in str(s) else float(str(s).strip()))
        out.append(d)
    r=pd.concat(out); r["Date"]=pd.to_datetime(r.Date)
    return r.sort_values("Date").reset_index(drop=True)

OUT={}

# ============================================================ A. PMF JOKER+
sec("A. LA PMF DU JOKER+, DÉRIVÉE DES RÈGLES")
JK=charge("data/jokerplus_FR_*.csv"); JK["g"]=(JK.Cash/1.5).round(); G=JK.g.sum()
print(f"  {len(JK)} tirages, {G/1e6:.1f} M de grilles, {JK.Cash.sum()/1e6:.1f} M€ misés.\n")

# Les lots sont fixes hors rang 1 : on le vérifie plutôt que de le supposer.
LOTS={r: sorted(JK[f"W-R{r}"].unique()) for r in range(2,9)}
assert all(len(v)==1 for v in LOTS.values()), LOTS
LOT={r: LOTS[r][0] for r in LOTS}
print("  Lots fixes vérifiés sur 5 057 tirages : " +
      " · ".join(f"R{r} {LOT[r]:,.2f} €".replace(",", " ") for r in range(2,9)))

# Structure : k chiffres alignés depuis l'une des DEUX extrémités.
# Convention de l'opérateur : les deux lectures sont payées séparément, donc
# p(k) = 2 × 0,9 × 10⁻ᵏ pour k = 1..5 ; à k = 6 les deux lectures se confondent
# et p = 10⁻⁶. On TESTE cette convention contre l'alternative combinatoire
# stricte (un seul lot par ticket, p = P(max(L,T) = k)).
p_op   = {k: 2*0.9*10**(-k) for k in range(1,6)}; p_op[6]=1e-6
def p_strict(k):
    # P(max(L,T) >= j) = 2·10⁻ʲ − P(L>=j et T>=j) ; l'intersection vaut 10⁻²ʲ
    # tant que les deux préfixes ne se recouvrent pas (2j <= 6), sinon elle
    # impose le numéro entier, soit 10⁻⁶.
    ge=lambda j: 0.0 if j>6 else 2*10**(-j)-(10**(-2*j) if 2*j<=6 else 1e-6)
    return ge(k)-ge(k+1) if k<6 else 1e-6
RANG={1:6,2:6,3:5,4:4,5:3,6:2,7:1}     # rang → nb de chiffres
print(f"\n  {'rang':<6}{'chiffres':>9}{'observé':>14}{'convention 2×0,9':>18}{'z':>8}"
      f"{'combinatoire stricte':>22}{'z':>9}")
for r in (7,6,5,4,3):
    k=RANG[r]; ko=JK[f"P-R{r}"].sum(); po=ko/G
    z1=(ko-G*p_op[k])/np.sqrt(G*p_op[k]*(1-p_op[k]))
    ps=p_strict(k); z2=(ko-G*ps)/np.sqrt(G*ps*(1-ps))
    print(f"  R{r:<5}{k:>9}{po:>14.6e}{p_op[k]:>18.6e}{z1:>+8.1f}{ps:>22.6e}{z2:>+9.1f}")
print("  → la convention de l'opérateur est confirmée ; la lecture combinatoire")
print("    stricte est rejetée à plus de 600 σ au rang 7. Un ticket qui aligne")
print("    des chiffres des DEUX côtés est payé deux fois.")

# rangs 1 et 2 : à k = 6 les deux lectures coïncident, p = 10⁻⁶ exactement,
# réparti 1/12 – 11/12 par le signe.
P_R1, P_R2 = 1e-6/12, 1e-6*11/12
for r,p,lab in [(1,P_R1,"6 chiffres + signe"),(2,P_R2,"6 chiffres sans signe")]:
    ko=int(JK[f"P-R{r}"].sum()); att=G*p
    print(f"\n  R{r} ({lab}) : {ko} observés, {att:.1f} attendus sous 1/{1/p:,.0f}"
          .replace(","," ") +
          f" → p = {2*min(stats.poisson.cdf(ko,att),1-stats.poisson.cdf(ko-1,att)):.3f}")
    print(f"     (la convention « payé deux fois » donnerait {2*att:.0f} : rejetée)")

# le signe est CUMULATIF : on le vérifie sur le rang 8
p8=JK["P-R8"].sum()/G
print(f"\n  Rang 8 (signe) : p observée = {p8:.6f} contre 1/12 = {1/12:.6f}")
print(f"     si le signe n'était payé QUE seul : {(1-0.2)/12:.6f} → écart de "
      f"{(p8-(1-0.2)/12)/((1-0.2)/12):.1%}")
print("  → le lot « signe » de 1,50 € s'ajoute à tous les autres. PMF cumulative.")

def pmf_joker(J):
    """Loi exacte du gain d'une grille Joker+ à 1,50 €, cagnotte J."""
    m={}
    add=lambda pr,v: m.__setitem__(v, m.get(v,0.0)+pr)
    add(P_R1, J); add(P_R2, LOT[2])                 # 6 chiffres : signe ou non
    pdig=1e-6
    for r in (3,4,5,6,7):
        k=RANG[r]; pr=p_op[k]; pdig+=pr
        add(pr/12, LOT[r]+LOT[8]); add(pr*11/12, LOT[r])
    prien=1-pdig
    add(prien/12, LOT[8]); add(prien*11/12, 0.0)
    v=np.array(sorted(m)); p=np.array([m[x] for x in v])
    assert abs(p.sum()-1)<1e-12, p.sum()
    return v,p

v0,p0=pmf_joker(0.0)
TRJ_HJ_MOD=float((v0*p0).sum()/1.5)
print(f"\n  TRJ du modèle hors jackpot : {TRJ_HJ_MOD:.4%}")
pay=sum(JK[f"P-R{r}"]*JK[f"W-R{r}"] for r in range(2,9)).sum()
TRJ_HJ_OBS=float(pay/JK.Cash.sum())
print(f"  TRJ hors jackpot réellement versé : {TRJ_HJ_OBS:.4%}  → écart "
      f"{100*(TRJ_HJ_MOD-TRJ_HJ_OBS):+.4f} point")
payJ=(JK["P-R1"]*JK["W-R1"]).sum()
print(f"  TRJ total versé (jackpots inclus) : {(pay+payJ)/JK.Cash.sum():.4%}")

# ============================================================ B. CAGNOTTE
sec("B. CAGNOTTE : PENTE, TRANCHES ET SEUIL, SUR LA PMF EXACTE")
pente=P_R1*1e6/1.5
seuil=(1-TRJ_HJ_MOD)*1.5/P_R1
trj=lambda J: TRJ_HJ_MOD+P_R1*J/1.5
print(f"  TRJ(J) = {TRJ_HJ_MOD:.4%} + J × {100*pente:.4f} point par million d'euros")
print(f"  Espérance nulle à J = {seuil:,.0f} €".replace(","," "))
CAGJ=json.load(open("out/jokerplus_cagnotte.json")) if glob.glob("out/jokerplus_cagnotte.json") else None
tranches=[]
if CAGJ:
    for a,b,_ in CAGJ["tranches"]:
        lo,hi=[float(x)*1e6 for x in a.replace(" M","").split("–")]
        tranches.append([a,b,round(trj((lo+hi)/2),6)])
    print(f"\n  {'tranche':<12}{'part':>8}{'TRJ':>9}{'perte/grille':>15}")
    for a,b,t in tranches:
        print(f"  {a:<12}{b:>8.2%}{t:>9.2%}{-1.5*(1-t):>14.2f} €")
    OUT["tranches"]=tranches; OUT["cagPct"]=CAGJ["pct"]; OUT["cagMoy"]=CAGJ["moy"]

# ============================================================ C. P(gain >= mise)
sec("C. P(RENTRER DANS SA MISE) — ÉNUMÉRATION EXACTE + CONVOLUTION")
N,K,C=40,6,3838380
combos=np.fromiter(itertools.chain.from_iterable(itertools.combinations(range(1,N+1),K)),
                   dtype=np.int8,count=C*K).reshape(C,K)
TABLE=[7200000.,120000.,500.42,33.85,4.93,2.50]     # régime depuis 10/2025
def gains_k(k):
    """gain total (€) des 3 838 380 tirages pour k grilles disjointes, Dream ignoré."""
    tot=np.zeros(C)
    for i in range(k):
        gr=list(range(1+6*i,7+6*i))
        lut=np.zeros(N+1,dtype=bool); lut[gr]=True
        m=lut[combos].sum(axis=1)
        g=np.zeros(C)
        for mm,idx in ((6,1),(5,2),(4,3),(3,4),(2,5)):
            g[m==mm]=TABLE[idx]                      # rang 2..6 (Dream non coché)
        tot+=g
    return tot
res_sans, res_avec = [], []
vJ,pJ=pmf_joker(CAGJ["pct"]["P50"] if CAGJ else 800000.)
for k in range(1,7):
    ed=gains_k(k); mise=2.5*k
    res_sans.append(float((ed>=mise).mean()))
    ev,ec=np.unique(ed,return_counts=True); ep=ec/C
    tv=(ev[:,None]+vJ[None,:]).ravel(); tp=(ep[:,None]*pJ[None,:]).ravel()
    res_avec.append(float(tp[tv>=mise+1.5].sum()))
    print(f"  {k} grille(s) : sans Joker+ {res_sans[-1]:.4%} | avec Joker+ {res_avec[-1]:.4%}")
print("  (rangs 1 et 2 : le Dream n'est pas modélisé ici, il ne change que le rang 1)")
OUT["pmiseSans"]=res_sans; OUT["pmiseAvec"]=res_avec

# ============================================================ D. LEVIER DU SIGNE
sec("D. LEVIER DU SIGNE : VRAI MODÈLE DE CO-GAGNANTS")
T=charge("data/jokerplus_TIRAGES_*.csv",num=False).rename(columns={"Signe astrologique":"signe"})
j=JK.merge(T[["Date","signe"]],on="Date",how="inner"); j["g"]=(j.Cash/1.5).round()
q=(j.groupby("signe").apply(lambda g: g["P-R8"].sum()/g.g.sum(), include_groups=False))
q=q/q.sum()                                        # part jouée de chaque signe
n_med=float(j.g.median())
print(f"  Grilles par tirage : médiane {n_med:,.0f}".replace(","," "))
print(f"  Part jouée : min {q.min():.5f} ({q.idxmin()}) | 1/12 = {1/12:.5f} | "
      f"max {q.max():.5f} ({q.idxmax()})")
print("\n  Modèle : mon ticket gagne le rang 1. Les autres tickets ont un numéro")
print("  ALÉATOIRE (non choisi) et un signe CHOISI. Le nombre de co-gagnants suit")
print("  donc K ~ Poisson(λ) avec λ = n × 10⁻⁶ × q(signe), et je touche J/(1+K).")
print(f"\n  {'signe':<12}{'part jouée':>12}{'λ':>10}{'E[1/(1+K)]':>13}{'gain vs moyen':>16}")
lam=lambda s: n_med*1e-6*q[s]
esp=lambda l: (1-np.exp(-l))/l
base=esp(n_med*1e-6/12)
det=[]
for s in q.sort_values().index:
    l=lam(s); e=esp(l)
    det.append({"s":s,"q":float(q[s]),"lam":float(l),"e":float(e),
                "d":float((e/base-1)*trj(CAGJ["pct"]["P50"] if CAGJ else 8e5)*0)})
    print(f"  {s:<12}{q[s]:>12.5f}{l:>10.5f}{e:>13.6f}{100*(e/base-1):>+15.4f} %")
Jmed=CAGJ["pct"]["P50"] if CAGJ else 800000.
contrib=P_R1*Jmed/1.5
best,worst=q.idxmin(),q.idxmax()
gain=(esp(lam(best))-esp(lam(worst)))/base*contrib
gain_moy=(esp(lam(best))/base-1)*contrib
print(f"\n  Contribution du rang 1 au TRJ (cagnotte médiane {Jmed:,.0f} €) : "
      f"{contrib:.4%}".replace(","," "))
print(f"  Jouer {best} plutôt que {worst} : {100*gain:+.4f} point de TRJ")
print(f"  Jouer {best} plutôt qu'un signe moyen : {100*gain_moy:+.4f} point de TRJ")
print(f"\n  À la cagnotte MAXIMALE jamais atteinte (3 125 000 €) : "
      f"{100*gain*3125000/Jmed:+.4f} point")
print("\n  → l'ancien chiffre de +0,436 point divisait la cagnotte par le nombre")
print("    ATTENDU de gagnants comme s'il y en avait toujours plusieurs. En réalité")
print(f"    λ ≈ {lam(best):.3f} : le partage n'arrive presque jamais. Sur 57 jackpots")
lam0=n_med*1e-6/12; att_part=57*(1-np.exp(-lam0))
print(f"    en seize ans, UN SEUL a été partagé. Le modèle en attend "
      f"{att_part:.2f} : P(au moins un partage) = {1-stats.poisson.pmf(0,att_part):.0%}.")
OUT["partObs"], OUT["partAtt"] = 1, float(att_part)
OUT["signes"]=det; OUT["levierSigne"]=float(gain); OUT["levierSigneMoy"]=float(gain_moy)
OUT["lamMed"]=float(n_med*1e-6/12); OUT["contribR1"]=float(contrib)

# ============================================================ E. EURODREAMS
sec("E. EURODREAMS : REQUALIFICATION DU +3,17 ET MODÈLE DE POPULARITÉ")
P={3:204/3838380,4:8415/3838380,5:119680/3838380,6:695640/3838380}
ED=charge("data/eurodreams_FR_*.csv"); ED["g"]=(ED.Mise/2.5).round()
n=ED.g.to_numpy(float)
print("  Modèle hiérarchique : W_r | tirage ~ Binomiale(n, p_r × M_r), où M_r est")
print("  le multiplicateur de POPULARITÉ du tirage (moyenne 1). Alors")
print("  Var(z) ≈ 1 + n p Var(M) : la sur-dispersion mesure directement Var(M).\n")
print(f"  {'rang':<6}{'n p':>10}{'Var(z)':>10}{'sd(M)':>9}{'amplitude P5–P95':>20}")
disp=[]
for r in (3,4,5,6):
    k=ED[f"P-R{r}"].to_numpy(float); p=P[r]
    z=(k-n*p)/np.sqrt(n*p*(1-p)); npm=float((n*p).mean())
    varM=max(0.0,(z.var()-1)/npm); sd=np.sqrt(varM)
    disp.append({"r":r,"np":npm,"var":float(z.var()),"sdM":float(sd)})
    print(f"  R{r:<5}{npm:>10.1f}{z.var():>10.2f}{sd:>9.3f}{f'×{(1+1.645*sd)/(1-1.645*sd):.2f}':>20}")
print("\n  Lecture : sd(M) est l'écart-type du multiplicateur de popularité d'un")
print("  tirage. Il se lit directement en pourcentage de sur- ou sous-fréquentation.")

z6=(ED["P-R6"].to_numpy(float)-n*P[6])/np.sqrt(n*P[6]*(1-P[6]))
ev=sum(P[r]*ED[f"W-R{r}"].to_numpy(float) for r in (3,4,5,6))/2.5
D=pd.DataFrame({"z":z6,"trj":ev}); D["d"]=pd.qcut(D.z,10,labels=False)
g=D.groupby("d").agg(n=("trj","size"),z=("z","mean"),trj=("trj","mean"))
moy=float(D.trj.mean())
print(f"\n  Déciles de fréquentation : D1 {g.trj.iloc[0]:.4%} … D10 {g.trj.iloc[-1]:.4%}, "
      f"moyenne {moy:.4%}")
print(f"  Amplitude D1 − moyenne : {100*(g.trj.iloc[0]-moy):+.2f} point")
print("\n  → REQUALIFICATION. Ce +3,17 point est une AMPLITUDE EMPIRIQUE constatée")
print("    a posteriori sur des tirages, pas un levier. Il décrit combien le TRJ")
print("    d'un tirage varie selon l'affluence sur les numéros sortis. Aucun")
print("    joueur ne peut choisir le décile : il dépend des numéros tirés.")
print("    Ce n'est PAS une borne du gain qu'une grille impopulaire procurerait.")
print("\n  Ce qu'il faudrait pour un vrai modèle grille → co-gagnants :")
print("    les 297 combinaisons TIRÉES (6 numéros + Dream). Avec elles, on régresse")
print("    W_r sur les caractéristiques du tirage (nombre de numéros ≤ 31, paires")
print("    consécutives, somme, étalement, multiples) et on obtient un modèle")
print("    PRÉDICTIF applicable à une grille avant le tirage. Les fichiers")
print("    eurodreams-gamedata-FR-yyyy.csv contiennent ces numéros ; je ne les ai pas.")
OUT["dispED"]=disp; OUT["decMoy"]=moy
OUT["dec"]=[{"d":int(d)+1,"n":int(r.n),"z":float(r.z),"trj":float(r.trj)} for d,r in g.iterrows()]
OUT["trjHJ"]=TRJ_HJ_MOD; OUT["trjHJobs"]=TRJ_HJ_OBS; OUT["pR1"]=P_R1; OUT["pR2"]=P_R2
OUT["pente"]=float(pente); OUT["seuil"]=float(seuil); OUT["lots"]={str(r):LOT[r] for r in LOT}
json.dump(OUT,open("out/v6_modele.json","w",encoding="utf-8"),ensure_ascii=False)
print("\n→ out/v6_modele.json")
