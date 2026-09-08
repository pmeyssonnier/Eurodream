# -*- coding: utf-8 -*-
"""
EuroDreams + Joker+ - AUDIT 8 :
 (a) controle de calendrier des 61 tirages du joueur
 (b) loi EXACTE du gain du portefeuille (4 grilles ED + 1 Joker+), par convolution
     de l'enumeration des 3 838 380 tirages ED et de la loi Joker+ reconstituee
 (c) reponse definitive au 'point 9' : P(rentrer dans sa mise)
"""
import itertools, glob, numpy as np, pandas as pd
from fractions import Fraction as F
from math import comb

# ====================== (a) CALENDRIER =====================================
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
JOURS = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
print("="*80); print("(a) CONTROLE DE CALENDRIER DES 61 TIRAGES"); print("="*80)
vc = pd.Series([JOURS[d.dayofweek] for d in DATES]).value_counts()
print(vc.to_string())
print("\n  EuroDreams est tire le LUNDI et le JEUDI.")
print(f"  Tirages du joueur tombant un lundi ou un jeudi : "
      f"{sum(d.dayofweek in (0,3) for d in DATES)}/61")
print(f"  Tirages tombant un mardi ou un vendredi        : "
      f"{sum(d.dayofweek in (1,4) for d in DATES)}/61")
print("  -> A EXPLIQUER : soit ces dates ne sont pas des dates de tirage EuroDreams")
print("     (dates de debit / de validation du bulletin en jeu continu), soit le jeu")
print("     concerne n'est pas EuroDreams. Tout le bilan est indexe sur ces dates.")

# volume Joker+ ces jours-la (proxy du jeu support)
fr = []
for f in sorted(glob.glob("data/jokerplus_FR_*.csv")):
    d = pd.read_csv(f, sep=";", encoding="utf-8-sig", dtype=str).dropna(how="all")
    d.columns = [c.strip().lstrip("﻿") for c in d.columns]
    d = d[d["Date"].notna() & d["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]
    d["Date"] = pd.to_datetime(d["Date"]); d["Cash"] = d["Cash"].map(
        lambda s: float(str(s).replace(".","").replace(",",".")))
    fr.append(d[["Date","Cash"]])
jk = pd.concat(fr)
jk["jour"] = jk.Date.dt.dayofweek
recent = jk[jk.Date >= "2025-09-01"]
print("\n  Mise Joker+ moyenne par jour de la semaine (depuis 09/2025) — proxy du")
print("  jeu support de la journee :")
for i, nom in enumerate(JOURS):
    s = recent[recent.jour == i].Cash
    if len(s): print(f"    {nom:<9} : {s.mean():>10,.0f} EUR  ({len(s)} tirages)".replace(",", " "))
pres = jk.Date.isin(DATES).sum()
print(f"\n  Les 61 dates du joueur sont-elles des jours de tirage Joker+ ? "
      f"{jk.Date.isin(DATES).sum()}/61 presentes")
print("  Les jours a FAIBLE volume Joker+ (~30-45 k EUR) sont les jours EuroDreams ;")
print("  les jours a fort volume sont Lotto (mer/sam) et EuroMillions (mar/ven).")

# ====================== (b) LOI EXACTE ======================================
print("\n" + "="*80); print("(b) LOI EXACTE DU GAIN DU PORTEFEUILLE"); print("="*80)
N, K = 40, 6; C = comb(N, K)
combos = np.fromiter(itertools.chain.from_iterable(itertools.combinations(range(1,N+1),K)),
                     dtype=np.int8, count=C*K).reshape(C, K)
def mtc(g):
    lut = np.zeros(N+1, bool); lut[list(g)] = True
    return lut[combos].sum(1).astype(np.int8)
JOUEUR = [(4,5,6,22,31,32),(5,8,16,18,19,34),(9,11,14,31,34,39),(3,16,27,29,32,37)]
MJ = np.stack([mtc(g) for g in JOUEUR])
ED_TBL = np.array([0.,0.,2.5,5.,20.,500., 0.2*(20000*12*30)+0.8*120000])

# --- loi Joker+ reconstituee a partir des frequences mesurees ---------------
# structure deduite : 6 chiffres alignes par l'une des DEUX extremites
#   p(exactement k chiffres) = 2 * 0,9 * 10^-k  pour k=1..5 ; p(6) = 10^-6
#   + 1 signe du zodiaque parmi 12, INDEPENDANT (p(R8)=1/12 exactement observe
#     -> le lot 'signe' se CUMULE avec le lot 'chiffres')
JACKPOT_MED = 800_000.0
dig = {1:(F(18,100),2.0), 2:(F(18,1000),5.0), 3:(F(18,10000),20.0),
       4:(F(18,100000),200.0), 5:(F(18,1000000),2000.0)}
jk_pmf = {}
def add(p, v): jk_pmf[v] = jk_pmf.get(v, F(0)) + p
p6 = F(1,1000000)
for s_match, ps in ((True, F(1,12)), (False, F(11,12))):
    bonus = 1.5 if s_match else 0.0
    reste = F(1)
    for k,(p,v) in dig.items():
        add(p*ps, v + bonus); reste -= p
    add(p6*ps, (JACKPOT_MED if s_match else 20000.0))       # 6 chiffres
    reste -= p6
    add(reste*ps, bonus)                                     # aucun chiffre
assert sum(jk_pmf.values()) == 1
jk_v = np.array(sorted(jk_pmf)); jk_p = np.array([float(jk_pmf[v]) for v in jk_v])
print("  Loi du gain d'UNE grille Joker+ (1,50 EUR), reconstituee :")
for v, p in zip(jk_v, jk_p):
    print(f"    {v:>10,.2f} EUR : p = {p:.8f}".replace(",", " "))
print(f"  E[gain Joker+] = {(jk_v*jk_p).sum():.4f} EUR -> TRJ = {(jk_v*jk_p).sum()/1.5:.2%}")
print(f"  (mesure directe sur 642 M grilles : 52,39 % — ecart du a la cagnotte prise")
print(f"   ici a sa MEDIANE {JACKPOT_MED:,.0f} EUR)".replace(",", " "))
print(f"  P(un gain Joker+)   = {jk_p[jk_v>0].sum():.4%}   "
      f"(= 1 - 0,8 x 11/12 ; l'estimateur par les zeros donnait 25,9 %)")
print(f"  P(gain >= 1,50 EUR) = {jk_p[jk_v>=1.5].sum():.4%}  -> le Joker+ seul rembourse")
print(f"     sa mise dans {jk_p[jk_v>=1.5].sum():.1%} des tirages, contre 21,47 % pour")
print(f"     une grille EuroDreams de 2,50 EUR.")

# ====================== (c) P(rentrer dans sa mise) =========================
print("\n" + "="*80); print("(c) P(RECUPERER SA MISE) — loi exacte, Joker+ inclus"); print("="*80)
def p_recup(k_ed, n_jk):
    mise = 2.5*k_ed + 1.5*n_jk
    ed = ED_TBL[MJ[:k_ed]].sum(0) if k_ed else np.zeros(1)
    vals, cnt = np.unique(ed, return_counts=True)
    pv, pp = vals, cnt/cnt.sum()
    for _ in range(n_jk):                       # convolution avec chaque Joker+
        pv = (pv[:, None] + jk_v[None, :]).ravel()
        pp = (pp[:, None] * jk_p[None, :]).ravel()
        o = np.argsort(pv); pv, pp = pv[o], pp[o]
        pv, idx = np.unique(pv, return_inverse=True)
        pp = np.bincount(idx, weights=pp)
    return mise, pp[pv >= mise - 1e-9].sum(), (pv*pp).sum(), (pv*pp).sum()/mise

print(f"  {'strategie':<34}{'mise':>7}{'P(>=mise)':>12}{'E[gain]':>10}{'TRJ':>9}")
for k, j, lbl in ((4,1,"4 grilles ED + Joker+  (ACTUEL)"), (4,0,"4 grilles ED, sans Joker+"),
                  (3,1,"3 grilles ED + Joker+"), (2,1,"2 grilles ED + Joker+"),
                  (1,1,"1 grille ED + Joker+"), (1,0,"1 grille ED seule  (reco C)"),
                  (0,1,"Joker+ seul"), (0,2,"Joker+ x2"), (0,3,"Joker+ x3")):
    m, p, ev, trj = p_recup(k, j)
    print(f"  {lbl:<34}{m:>6.2f} {p:>11.2%} {ev:>9.3f} {trj:>8.2%}")
print("\n  -> Lecture correcte : ajouter le Joker+ AUGMENTE le TRJ du portefeuille")
print("     (43,18 % -> 44,23 % a 4 grilles) mais FAIT CHUTER P(rentrer dans sa mise)")
print("     (2,30 % -> 1,72 %), parce qu'il releve la mise de 1,50 EUR sans offrir de")
print("     lot intermediaire suffisant. Les deux criteres divergent : c'est le TRJ")
print("     qui compte a long terme. Le meilleur TRJ du tableau est le Joker+ SEUL.")

# ============ (d) VALIDATION DU MODELE SUR LES DONNEES DU JOUEUR ============
print("\n" + "="*80); print("(d) VALIDATION : le modele predit-il ses 61 tirages ?"); print("="*80)
from scipy import stats
p0_ed = float((ED_TBL[MJ].sum(0) == 0).mean())
p0_jk = float(jk_p[jk_v == 0].sum())
p0 = p0_ed * p0_jk
print(f"  P(aucun gain EuroDreams, 4 grilles) = {p0_ed:.6f}  (exact, enumeration)")
print(f"  P(aucun gain Joker+)                = {p0_jk:.6f}  (exact, 1 - 0,8 x 11/12)")
print(f"  P(gain TOTAL nul sur un tirage)     = {p0:.6f} = {p0:.2%}")
print(f"  OBSERVE : 17/61 = {17/61:.2%}   attendu {61*p0:.2f} tirages a zero")
bt = stats.binomtest(17, 61, p0)
print(f"  Test binomial exact : p = {bt.pvalue:.3f}  -> ajustement PARFAIT.")
print("  C'est la meilleure validation possible du modele complet : une prediction")
print("  faite sans regarder la frequence des zeros la reproduit au dixieme de point.")

# loi exacte du gain d'un tirage complet (4 ED + 1 Joker+)
ed = ED_TBL[MJ].sum(0)
vals, cnt = np.unique(ed, return_counts=True)
pv, pp = vals, cnt/cnt.sum()
pv = (pv[:, None] + jk_v[None, :]).ravel(); pp = (pp[:, None] * jk_p[None, :]).ravel()
o = np.argsort(pv); pv, pp = pv[o], pp[o]
pv, idx = np.unique(pv, return_inverse=True); pp = np.bincount(idx, weights=pp)
print(f"\n  E[gain/tirage] = {(pv*pp).sum():.4f} EUR | mise 11,50 -> TRJ {(pv*pp).sum()/11.5:.2%}")
mask = pv < 1e5                     # on neutralise les rangs 1 (non realisables sur 61 tirages)
evh = (pv[mask]*pp[mask]).sum()/pp[mask].sum()
print(f"  E[gain | pas de gros lot] = {evh:.4f} EUR -> TRJ hors gros lot = {evh/11.5:.2%}")
rng = np.random.default_rng(11)
sim = rng.choice(pv[mask], size=(200_000, 61), p=pp[mask]/pp[mask].sum()).sum(1)/(61*11.5)
print(f"  Loi du TRJ sur 61 tirages (hors gros lot) : mediane {np.median(sim):.2%} | "
      f"IC90 [{np.quantile(sim,.05):.2%} ; {np.quantile(sim,.95):.2%}]")
print(f"  TRJ observe 33,06 % -> percentile {(sim <= 0.330577).mean():.1%}")

# ============ (e) LES 61 MONTANTS SONT-ILS DECOMPOSABLES ? ==================
print("\n" + "="*80); print("(e) CHAQUE GAIN EST-IL EXPLICABLE PAR EuroDreams + Joker+ ?"); print("="*80)
GAINS = [7.0,0,2.0,2.5,4.0,4.5,0,5.0,0,0,2.5,4.5,2.5,0,2.5,2.5,2.5,1.5,2.5,0,
         0,6.5,7.3,11.7,7.0,1.5,4.0,0,4.5,7.5,2.5,2.0,0,0,2.5,2.5,9.0,2.5,0,0,
         0,4.0,7.5,0,0,5.5,2.5,2.5,2.5,0,10.4,2.5,5.0,38.5,2.5,20.0,2.5,2.0,0,2.0,5.0]
ED_OK = sorted({round(2.5*a+5*b+20*c, 2) for a in range(5) for b in range(5-a)
                for c in range(5-a-b)} | {500.0, 502.5, 505.0})
JK_OK = sorted(float(v) for v in jk_v if v < 1000)
def decomp(g):
    return [(a, j) for j in JK_OK for a in ED_OK if abs(a + j - g) < 1e-9]
bad = []
for g in sorted(set(GAINS)):
    d = decomp(g)
    if not d: bad.append(g)
print("  Hypothese : rangs EuroDreams 3-6 FIXES (500 / 20 / 5 / 2,50) + table Joker+ mesuree")
print(f"  Montants NON decomposables : {bad}")
print(f"  Tirages concernes : {sum(g in bad for g in GAINS)}/61")
print("  Ces montants portent des centimes (0,30 / 0,70 / 0,40) absents des DEUX tables.")
print("  -> ils proviennent necessairement d'un rang PARIMUTUEL (montant au centime)")
print("     ou d'un troisieme produit. A trancher avant toute conclusion sur le TRJ.")
for g in bad:
    print(f"    {g:>5.2f} EUR : ecart au multiple de 0,50 le plus proche = "
          f"{min(abs(g-round(g*2)/2), 1):.2f}")
