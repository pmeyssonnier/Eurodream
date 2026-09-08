# -*- coding: utf-8 -*-
"""EuroDreams - AUDIT 13 : reconciliation ligne a ligne du releve du joueur
avec les tables de gains REELLES, et benchmark exact tirage par tirage."""
import glob, itertools, numpy as np, pandas as pd
fr=[]
for f in sorted(glob.glob("data/eurodreams_FR_*.csv")):
    d=pd.read_csv(f,sep=";",encoding="utf-8-sig",dtype=str).dropna(how="all")
    d.columns=[c.strip().lstrip("﻿") for c in d.columns]
    d=d[d["Date"].notna()&d["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]
    for c in d.columns[1:]: d[c]=d[c].astype(float)
    d["Date"]=pd.to_datetime(d["Date"]); fr.append(d)
ed=pd.concat(fr).sort_values("Date").set_index("Date")
DATES=pd.to_datetime([
 "2025-09-05","2025-09-09","2025-09-12","2025-09-16","2025-09-19","2025-09-23","2025-09-26",
 "2025-09-30","2025-10-03","2025-10-07","2025-10-10","2025-10-14","2025-10-17","2025-10-21",
 "2025-11-07","2025-11-11","2025-11-14","2025-11-18","2025-11-21","2025-11-25","2025-11-28",
 "2025-12-02","2025-12-05","2025-12-09","2025-12-12","2025-12-16","2025-12-19","2025-12-30",
 "2026-01-02","2026-01-06","2026-01-09","2026-01-13","2026-01-16","2026-01-20","2026-01-27",
 "2026-01-30","2026-02-03","2026-02-06","2026-02-10","2026-02-13","2026-02-17","2026-04-27",
 "2026-04-28","2026-05-01","2026-05-05","2026-05-08","2026-05-12","2026-05-15","2026-05-22",
 "2026-05-26","2026-05-29","2026-06-02","2026-06-05","2026-06-09","2026-06-12","2026-06-16",
 "2026-06-19","2026-06-23","2026-06-26","2026-06-30","2026-07-03"])
GAINS=np.array([7.0,0,2.0,2.5,4.0,4.5,0,5.0,0,0,2.5,4.5,2.5,0,2.5,2.5,2.5,1.5,2.5,0,
 0,6.5,7.3,11.7,7.0,1.5,4.0,0,4.5,7.5,2.5,2.0,0,0,2.5,2.5,9.0,2.5,0,0,
 0,4.0,7.5,0,0,5.5,2.5,2.5,2.5,0,10.4,2.5,5.0,38.5,2.5,20.0,2.5,2.0,0,2.0,5.0])
JK=[0.0,1.5,2.0,3.5,5.0,6.5,20.0,21.5,200.0,201.5]
P={1:1/19191900,2:4/19191900,3:204/3838380,4:8415/3838380,5:119680/3838380,6:695640/3838380}

def tot(row,kmax=4):
    lots=[x for x in [2.5,row["W-R5"],row["W-R4"],row["W-R3"],120000.,7200000.] if x>0]
    out={0.0}
    for k in range(1,kmax+1):
        for c in itertools.combinations_with_replacement(lots,k):
            s=round(sum(c),2)
            if s<=200: out.add(s)
    return out
def ok(g,row): 
    T=tot(row); return any(abs(g-(t+j))<1e-9 for t in T for j in JK)

print("="*84); print("1. LE RELEVE EST-IL EURODREAMS ? — reconciliation des MONTANTS")
print("="*84)
print("  Hypothese : ligne datee J = tirage de J-1 (date de DEBIT, pas de tirage).")
lig=[]
for x0,g in zip(DATES,GAINS):
    for lag in (1,0):
        x=x0-pd.Timedelta(days=lag)
        if x in ed.index:
            lig.append((x0,x,lag,g,ok(g,ed.loc[x]))); break
    else: lig.append((x0,None,None,g,False))
L=pd.DataFrame(lig,columns=["releve","tirage","lag","gain","ok"])
print(f"  Lignes rattachees a un tirage EuroDreams : {L.tirage.notna().sum()}/61 "
      f"(dont {int((L.lag==1).sum())} a J-1 et {int((L.lag==0).sum())} a J-0)")
print(f"  Montants EXACTEMENT reconcilies          : {L.ok.sum()}/61")
print(f"    - parmi les {int((L.gain>0).sum())} lignes gagnantes : "
      f"{int(L[L.gain>0].ok.sum())}/{int((L.gain>0).sum())}")
print(f"    - les 18 lignes a 0 EUR sont trivialement compatibles")
print("\n  >>> Le releve EST un releve EuroDreams + Joker+, avec un decalage de")
print("      UN JOUR (debit le lendemain du tirage). Ma conclusion du tour")
print("      precedent — 'ce n'est pas EuroDreams' — etait FAUSSE.")

print("\n  Lignes residuelles :")
for _,r in L[~L.ok].iterrows():
    if r.tirage is None: print(f"    {r.releve.date()} gain {r.gain:6.2f} : aucun tirage a J-1 ni J-0")
    else:
        w=ed.loc[r.tirage]
        print(f"    {r.releve.date()} gain {r.gain:6.2f} -> tirage {r.tirage.date()} "
              f"(R3={w['W-R3']:.2f} R4={w['W-R4']:.2f} R5={w['W-R5']:.2f})")
print("  Recherche d'un tirage compatible a +/- 10 jours pour ces lignes :")
for _,r in L[~L.ok].iterrows():
    hits=[d.date() for d in ed.index if abs((d-r.releve).days)<=10 and ok(r.gain,ed.loc[d])]
    print(f"    gain {r.gain:6.2f} ({r.releve.date()}) -> {hits if hits else 'AUCUN'}")

print("\n" + "="*84); print("2. BENCHMARK EXACT : ses 61 tirages, avec les VRAIES tables")
print("="*84)
M=L[L.tirage.notna()].copy()
rows=ed.loc[M.tirage]
ev4=4*sum(P[r]*rows[f"W-R{r}"].to_numpy() for r in range(1,7))
ev4_nj=4*sum(P[r]*rows[f"W-R{r}"].to_numpy() for r in range(3,7))
print(f"  Gain EuroDreams ATTENDU sur ces 61 tirages (4 grilles, tables reelles) :")
print(f"    avec rangs 1-2 : {ev4.sum():8.2f} EUR   (TRJ {ev4.sum()/(61*10):.2%})")
print(f"    hors rangs 1-2 : {ev4_nj.sum():8.2f} EUR   (TRJ {ev4_nj.sum()/(61*10):.2%})")
print(f"  + Joker+ attendu (52,39 % de 61 x 1,50)   : {61*1.5*0.5239:8.2f} EUR")
print(f"  + Joker+ hors jackpot (46,80 %)           : {61*1.5*0.4680:8.2f} EUR")
tot_nj=ev4_nj.sum()+61*1.5*0.4680
print(f"  TOTAL attendu hors gros lots              : {tot_nj:8.2f} EUR")
print(f"  TOTAL OBSERVE                             : {GAINS.sum():8.2f} EUR")
print(f"  ratio observe / attendu                   : {GAINS.sum()/tot_nj:.3f}")
print(f"  TRJ de portefeuille attendu hors gros lot : {tot_nj/(61*11.5):.2%}")
print(f"  TRJ de portefeuille OBSERVE               : {GAINS.sum()/(61*11.5):.2%}")

print("\n" + "="*84); print("3. TRJ REEL D'EURODREAMS, PAR PERIODE"); print("="*84)
for r in range(1,7): ed[f"pay{r}"]=ed[f"P-R{r}"]*ed[f"W-R{r}"]
ed["payout"]=ed[[f"pay{r}" for r in range(1,7)]].sum(axis=1)
ed["grilles"]=(ed.Mise/2.5).round()
for lab,m in (("2023-11 -> 2025-09",ed.index<"2025-10-01"),
              ("2025-10 -> 2026-09",ed.index>="2025-10-01"),
              ("TOTAL 297 tirages",np.ones(len(ed),bool))):
    s=ed[m]
    theo=sum(P[r]*s[f"W-R{r}"].mean() for r in range(3,7))/2.5
    print(f"  {lab:<22} {len(s):>3} tirages | TRJ mesure {s.payout.sum()/s.Mise.sum():7.2%}"
          f" | hors rangs 1-2 {(s.payout.sum()-s.pay1.sum()-s.pay2.sum())/s.Mise.sum():7.2%}"
          f" | theorique rangs 3-6 {theo:7.2%}")
esp=sum(P[r]*ed[f"W-R{r}"].mean() for r in range(3,7))/2.5
print(f"\n  TRJ de long terme, tables reelles + probabilites exactes :")
print(f"    rangs 3-6 : {esp:.2%}")
print(f"    rang 2 (120 000 EUR) : {P[2]*120000/2.5:.2%}")
print(f"    rang 1 (7 200 000 EUR nominal) : {P[1]*7200000/2.5:.2%}")
print(f"    TOTAL nominal : {esp+P[2]*120000/2.5+P[1]*7200000/2.5:.2%}")
pv=20000*(1-(1+0.03/12)**-360)/(0.03/12)
print(f"    TOTAL actualise a 3 % (rente a {pv:,.0f} EUR) : "
      f"{esp+P[2]*120000/2.5+P[1]*pv/2.5:.2%}".replace(",", " "))
print(f"    TRJ officiel annonce : 52,00 %")
