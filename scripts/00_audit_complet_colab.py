# -*- coding: utf-8 -*-
# ============================================================================
#  LEGACY — NE PLUS UTILISER TEL QUEL.
#  Ce script date de la premiere passe, avant l'exploitation des 297 tirages
#  officiels. Il repose sur la table de gains SUPPOSEE (R3 = 500 EUR, R4 = 20/30,
#  R5 = 5 fixes) alors que les rangs 3, 4 et 5 sont PARIMUTUELS. Ses TRJ sont donc
#  faux d'environ 0,3 point. Remplace par les scripts 11 a 19.
#  Conserve pour tracer l'evolution de l'audit.
# ============================================================================
# ============================================================================
#  AUDIT CONTRADICTOIRE EuroDreams — script unique, copiable dans Google Colab
#  !pip -q install numpy scipy pandas
#  Duree ~45 s, RAM ~300 Mo. Toutes les probas de jeu sont EXACTES (enumeration
#  des 3 838 380 tirages), pas de Monte-Carlo sur la combinatoire.
# ============================================================================
import itertools
import numpy as np, pandas as pd
from math import comb
from scipy import stats

N, K, D = 40, 6, 5
C, CT = comb(N, K), comb(N, K)*D
MISE_G, MISE_JK = 2.50, 1.50
JOUEUR = [(4,5,6,22,31,32), (5,8,16,18,19,34), (9,11,14,31,34,39), (3,16,27,29,32,37)]
DISJOINT = [(1,2,3,4,5,6), (7,8,9,10,11,12), (13,14,15,16,17,18), (19,20,21,22,23,24)]
GAINS = np.array([7.0,0,2.0,2.5,4.0,4.5,0,5.0,0,0,2.5,4.5,2.5,0,2.5,2.5,2.5,1.5,2.5,0,
                  0,6.5,7.3,11.7,7.0,1.5,4.0,0,4.5,7.5,2.5,2.0,0,0,2.5,2.5,9.0,2.5,0,0,
                  0,4.0,7.5,0,0,5.5,2.5,2.5,2.5,0,10.4,2.5,5.0,38.5,2.5,20.0,2.5,2.0,0,2.0,5.0])
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
n = len(GAINS); MISE_T = 4*MISE_G + MISE_JK
def sec(t): print("\n" + "="*76 + f"\n{t}\n" + "="*76)

# ---------------------------------------------------------------- 1. RANGS
sec("1. PROBABILITES PAR RANG — combinatoire exacte")
hyp = {m: comb(K, m)*comb(N-K, K-m) for m in range(K+1)}
assert sum(hyp.values()) == C
RANGS = [("R1","6+Dream",hyp[6],CT),("R2","6",hyp[6]*(D-1),CT),("R3","5",hyp[5],C),
         ("R4","4",hyp[4],C),("R5","3",hyp[3],C),("R6","2",hyp[2],C)]
P = {r: f/d for r,_,f,d in RANGS}
print(pd.DataFrame([dict(rang=r, cond=c, favorables=f, denom=d, p=f/d, un_sur=d/f)
                    for r,c,f,d in RANGS]).to_string(
      index=False, formatters={"p":"{:.4e}".format,"un_sur":"{:,.0f}".format}))
print(f"\nP(gain, 1 grille) = {sum(P.values()):.6f} = 1 sur {1/sum(P.values()):.3f}")

# ------------------------------------------------------------ 2. ESPERANCE
sec("2. ESPERANCE — rente nominale vs actualisee")
def pv(m, a, r): 
    return m*12*a if r == 0 else m*(1-(1+r/12)**(-12*a))/(r/12)
for r in (0.00, 0.02, 0.03):
    for r3, r4, lbl in ((500,30,"table audit (R4=30)"), (500,20,"table observee (R4=20)")):
        ev = (P["R1"]*pv(20000,30,r) + P["R2"]*pv(2000,5,r)
              + P["R3"]*r3 + P["R4"]*r4 + P["R5"]*5 + P["R6"]*2.5)
        print(f"  taux {r:.0%} | {lbl:<24} EV = {ev:.4f} EUR -> TRJ = {ev/MISE_G:6.2%}")
EV_G   = P["R1"]*20000*12*30 + P["R2"]*120000 + P["R3"]*500 + P["R4"]*20 + P["R5"]*5 + P["R6"]*2.5
EV_NR1 = EV_G - P["R1"]*20000*12*30
print(f"\n  Decomposition (nominal, R4=20) — part de chaque rang dans l'esperance :")
for r, g in (("R1",20000*12*30),("R2",120000),("R3",500),("R4",20),("R5",5),("R6",2.5)):
    print(f"    {r} : {P[r]*g:8.4f} EUR = {P[r]*g/EV_G:6.2%}")
print(f"  TRJ moyen = {EV_G/MISE_G:.2%} | TRJ HORS jackpot = {EV_NR1/MISE_G:.2%}")
print(f"  TRJ officiel annonce = 52,00 % -> ecart de {0.52-EV_G/MISE_G:.1%} pt.")
print(f"  Cet ecart est STRUCTUREL, pas inexplique : le reglement affecte 45,21 %")
print(f"  de l'argent des lots (= 52 % des mises) au Fonds de Reserve, qui finance")
print(f"  les rangs 1-2 et les promotions. Il reste 52 % x (1 - 45,21 %) = "
      f"{0.52*(1-0.4521):.4%}")
print(f"  pour les rangs 3-6, contre {EV_NR1/MISE_G:.4%} calcules ici sur la table")
print(f"  SUPPOSEE (28,44 % avec la table REELLE, cf. script 14). Les 52 % sont")
print(f"  exacts au niveau de la famille de jeux, faux pour un tirage ordinaire.")
seuil = (MISE_G - (EV_G - P["R1"]*20000*12*30))/P["R1"]
print(f"  Jackpot (valeur actuelle) requis pour EV>=mise : {seuil:,.0f} EUR".replace(",", " "))

# --------------------------------------------------- 3. ENUMERATION EXACTE
sec("3. ENUMERATION EXHAUSTIVE DES 3 838 380 TIRAGES")
combos = np.fromiter(itertools.chain.from_iterable(itertools.combinations(range(1,N+1),K)),
                     dtype=np.int8, count=C*K).reshape(C, K)
def mtc(g):
    lut = np.zeros(N+1, bool); lut[list(g)] = True
    return lut[combos].sum(1).astype(np.int8)
MJ, MD = np.stack([mtc(g) for g in JOUEUR]), np.stack([mtc(g) for g in DISJOINT])
R1AV = 0.2*(20000*12*30) + 0.8*120000            # moyenne sur le Dream
TBL  = np.array([0., 0., 2.5, 5., 20., 500., R1AV])
u = set().union(*map(set, JOUEUR))
print(f"Couverture joueur : {len(u)} numeros distincts / 40 ; doublons "
      f"{sorted(x for x in u if sum(x in set(g) for g in JOUEUR) > 1)}")
for k in range(1, 5):
    print(f"  {k} grille(s) : P(>=1 gain) = {(TBL[MJ[:k]].sum(0) > 0).mean():.4%}")
print(f"  4 grilles DISJOINTES : P(>=1 gain) = {(TBL[MD].sum(0) > 0).mean():.4%}")
p4 = (hyp[4]+hyp[5]+hyp[6])/C
print(f"  P(>=4 bons sur >=1 grille) : joueur {(MJ>=4).any(0).mean():.6%} | "
      f"disjointes {(MD>=4).any(0).mean():.6%} | 4xP1 = {4*p4:.6%}  (egalite EXACTE)")

sec("4. P(RECUPERER SA MISE) — robustesse (point 9 de l'audit)")
print("  Balayage du rang 5 ; rang 3 = 500 et rang 4 = 20 fixes")
rows = []
for r5 in (2.5, 4, 5, 6, 7.5, 10, 15):
    t = np.array([0.,0.,2.5,float(r5),20.,500.,R1AV])
    rows.append(dict(rang5=r5, **{f"k={k}": (t[MJ[:k]].sum(0) >= 2.5*k).mean() for k in range(1,5)}))
print(pd.DataFrame(rows).to_string(index=False, formatters={f"k={k}":"{:.2%}".format for k in range(1,5)}))
print("\n  Balayage du rang 4 (rang 5 = 5) puis du rang 3 : effet nul au-dela de 10 EUR")
for r4 in (5, 10, 20, 100):
    print(f"    R4={r4:>4} : " + " ".join(f"{(np.array([0.,0.,2.5,5.,float(r4),500.,R1AV])[MJ[:k]].sum(0)>=2.5*k).mean():7.4%}" for k in range(1,5)))
for r3 in (250, 5000):
    print(f"    R3={r3:>4} : " + " ".join(f"{(np.array([0.,0.,2.5,5.,20.,float(r3),R1AV])[MJ[:k]].sum(0)>=2.5*k).mean():7.4%}" for k in range(1,5)))
print("\n  Avec le Joker+ dans la mise (2,50k + 1,50) :")
print("    " + " ".join(f"k={k}:{(TBL[MJ[:k]].sum(0) >= 2.5*k+1.5).mean():.2%}" for k in range(1,5)))

# ------------------------------------------------------------- 5. LE BILAN
sec("5. BILAN DES 61 TIRAGES")
df = pd.DataFrame({"date": DATES, "gain": GAINS}); df["net"] = df.gain - MISE_T
df["solde"] = df.net.cumsum()
print(f"  mise {n*MISE_T:.2f} | gains {df.gain.sum():.2f} | solde {df.net.sum():.2f} | "
      f"TRJ {df.gain.sum()/(n*MISE_T):.4%}")
print(f"  moyenne {df.gain.mean():.3f} | ecart-type {df.gain.std(ddof=1):.3f} | "
      f"mediane {df.gain.median():.2f} | zeros {(df.gain==0).sum()} | >mise {(df.gain>MISE_T).sum()}")
print(f"  solde max = {df.solde.max():.2f} EUR (tirage n{df.solde.idxmax()+1})")
print("\n  TRJ par fenetre TERMINALE (k derniers)   vs   fenetre INITIALE (k premiers) :")
for k in (8, 28, 47, 61):
    print(f"    k={k:>3} : {df.tail(k).gain.sum()/(k*MISE_T):7.2%}   |   "
          f"{df.head(k).gain.sum()/(k*MISE_T):7.2%}")
print("    -> la 'decroissance' est un effet de RECENCE (les 2 gros gains sont a la fin),")
print("       pas une convergence. Le sens inverse donne une croissance.")

sec("6. INTERVALLE DE CONFIANCE DU TRJ (n=61)")
rng = np.random.default_rng(20260908)
boot = rng.choice(GAINS, size=(200_000, n)).mean(1)/MISE_T
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"  Bootstrap percentile 95 % : [{lo:.2%} ; {hi:.2%}]  -> LARGEUR {100*(hi-lo):.1f} pts")
se = GAINS.std(ddof=1)/np.sqrt(n)/MISE_T
print(f"  t de Student (indicatif)  : [{GAINS.mean()/MISE_T-stats.t.ppf(.975,n-1)*se:.2%} ; "
      f"{GAINS.mean()/MISE_T+stats.t.ppf(.975,n-1)*se:.2%}]")
for c, l in ((0.266,"26,6 % (mediane simulee)"),(0.2818,"28,2 % (hors jackpot)"),
             (0.4318,"43,2 % (esperance)"),(0.52,"52 % (annonce)")):
    print(f"    {l:<28} : {'DANS' if lo<=c<=hi else 'HORS'} l'IC")
print(f"  n necessaire pour un IC de largeur 5 pts : "
      f"{(2*1.96*GAINS.std(ddof=1)/(0.05*MISE_T))**2:,.0f} tirages".replace(",", " "))
rho, psp = stats.spearmanr(np.arange(n), GAINS)
print(f"  Tendance temporelle : Spearman rho={rho:+.3f} p={psp:.3f} -> aucune derive")

sec("7. LE JOUEUR EST-IL MALCHANCEUX ? (etalon hors jackpot)")
tbl0 = np.array([0.,0.,2.5,5.,20.,500.,0.])           # rangs 1-2 neutralises
sim = rng.choice(tbl0[MJ].sum(0), size=(200_000, n)).sum(1)/(n*4*MISE_G)
print(f"  Loi du TRJ EuroDreams sur 61 tirages : moyenne {sim.mean():.2%} | "
      f"mediane {np.median(sim):.2%} | IC90 [{np.quantile(sim,.05):.2%} ; {np.quantile(sim,.95):.2%}]")
ATT = sorted({round(2.5*a+5*b+20*c+500*d,2) for a in range(5) for b in range(5-a)
              for c in range(5-a-b) for d in range(5-a-b-c)})
ed_max = np.array([max([x for x in ATT if x <= g], default=0.) for g in GAINS])
print(f"  Part EuroDreams : bornee par [0 ; {ed_max.sum():.2f}] EUR -> TRJ_ED dans "
      f"[0 % ; {ed_max.sum()/(n*4*MISE_G):.2%}]")
print(f"  Percentile du joueur sous le modele : {(sim <= ed_max.sum()/(n*4*MISE_G)).mean():.1%}")
print("  -> il est AU-DESSUS de la mediane du modele, pas en-dessous.")
inc = [float(g) for g in np.unique(GAINS) if g not in ATT]
print(f"\n  {sum(g not in ATT for g in GAINS)}/{n} gains sont IMPOSSIBLES en EuroDreams seul")
print(f"  (montants {inc}) -> contamination Joker+ certaine.")
p_jk = 1 - (GAINS == 0).mean()/(1-(TBL[MJ].sum(0) > 0).mean())
print(f"  P(gain Joker+) estime par la frequence des zeros : {p_jk:.1%} des tirages.")

sec("8. BUDGET ANNUEL -> PERTE ESPEREE")
tir_an = n/(((DATES.max()-DATES.min()).days)/365.25)
print(f"  Rythme observe : {tir_an:.1f} tirages/an ({tir_an/104:.0%} du calendrier officiel)")
for k in (0,1,2,3,4):
    for jk in (0.0, MISE_JK):
        m = 2.5*k + jk
        if m == 0: continue
        print(f"    {k} grille(s) {'+ Joker+' if jk else '        '} : mise {m:5.2f} | "
              f"budget {m*tir_an:6.0f} EUR/an | perte esperee {(m-k*EV_G)*tir_an:6.0f} EUR/an "
              f"| perte hors jackpot {(m-k*EV_NR1)*tir_an:6.0f} EUR/an")
print("  (Joker+ compte a 0 : borne INFERIEURE du rendement, sa table est inconnue.)")
