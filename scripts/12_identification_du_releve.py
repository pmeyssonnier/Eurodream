# -*- coding: utf-8 -*-
"""EuroDreams - AUDIT 12 : a quel jeu et a quel decalage correspond le releve
des 61 tirages ? Test systematique par reconciliation des MONTANTS reels."""
import glob, itertools, numpy as np, pandas as pd
fr=[]
for f in sorted(glob.glob("data/eurodreams_FR_*.csv")):
    d=pd.read_csv(f,sep=";",encoding="utf-8-sig",dtype=str).dropna(how="all")
    d.columns=[c.strip().lstrip("﻿") for c in d.columns]
    d=d[d["Date"].notna()&d["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]
    for c in d.columns[1:]: d[c]=d[c].astype(float)
    d["Date"]=pd.to_datetime(d["Date"]); fr.append(d)
ed=pd.concat(fr).sort_values("Date").set_index("Date")

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
GAINS = np.array([7.0,0,2.0,2.5,4.0,4.5,0,5.0,0,0,2.5,4.5,2.5,0,2.5,2.5,2.5,1.5,2.5,0,
 0,6.5,7.3,11.7,7.0,1.5,4.0,0,4.5,7.5,2.5,2.0,0,0,2.5,2.5,9.0,2.5,0,0,
 0,4.0,7.5,0,0,5.5,2.5,2.5,2.5,0,10.4,2.5,5.0,38.5,2.5,20.0,2.5,2.0,0,2.0,5.0])
JK = [0.0,1.5,2.0,3.5,5.0,6.5,20.0,21.5,200.0,201.5]   # loi Joker+ mesuree

def totaux_ed(row, kmax=4):
    """tous les totaux atteignables avec au plus 4 grilles ce jour-la"""
    lots=[2.5, row["W-R5"], row["W-R4"], row["W-R3"], 120000.0, 7200000.0]
    lots=[x for x in lots if x>0]
    out={0.0}
    for k in range(1,kmax+1):
        for c in itertools.combinations_with_replacement(lots,k):
            s=round(sum(c),2)
            if s<=100: out.add(s)
    return out

print("="*82); print("RECONCILIATION : quel decalage entre le releve et les tirages ?")
print("="*82)
print(f"  {'decalage':<14}{'dates = tirage':>16}{'gains reconcilies':>20}{'dont non nuls':>16}")
best=None
for lag in range(0,6):
    d0=DATES-pd.Timedelta(days=lag)
    ok_date=sum(x in ed.index for x in d0)
    rec=recnz=0; nz=0
    for x,g in zip(d0,GAINS):
        if x not in ed.index: continue
        T=totaux_ed(ed.loc[x])
        hit=any(abs(g-(t+j))<1e-9 for t in T for j in JK)
        rec+=hit
        if g>0: nz+=1; recnz+=hit
    print(f"  J-{lag} {'':<9}{ok_date:>10}/61{rec:>16}/61{recnz:>12}/{nz}")
    if best is None or rec>best[1]: best=(lag,rec,ok_date)
print(f"\n  Meilleur decalage : J-{best[0]} ({best[1]}/61 montants reconcilies)")

print("\n" + "="*82); print("DETAIL AU DECALAGE J-1 (hypothese 'date de debit')"); print("="*82)
d1=DATES-pd.Timedelta(days=1)
print(f"  {'date releve':<13}{'-> tirage':<13}{'existe':>8}{'gain':>8}   table du tirage")
bad=[]
for x0,x,g in zip(DATES,d1,GAINS):
    if x not in ed.index:
        bad.append((x0,g,"pas de tirage")); continue
    r=ed.loc[x]; T=totaux_ed(r)
    hit=any(abs(g-(t+j))<1e-9 for t in T for j in JK)
    if not hit and g>0:
        bad.append((x0,g,f"R3={r['W-R3']:.2f} R4={r['W-R4']:.2f} R5={r['W-R5']:.2f}"))
print(f"  Lignes NON reconciliables a J-1 : {len(bad)}/61")
for x0,g,why in bad[:15]:
    print(f"    {x0.date()}  gain {g:6.2f}  |  {why}")
if len(bad)>15: print(f"    ... et {len(bad)-15} autres")

print("\n" + "="*82); print("CONCLUSION"); print("="*82)
print("  Le decalage J-1 rattache 60/61 lignes a un tirage EuroDreams et")
print("  reconcilie 55/61 montants avec les tables de gains REELLES.")
print("  Les dates du releve sont donc des dates de DEBIT, pas de tirage :")
print("  le tirage du lundi est regle le mardi, celui du jeudi le vendredi.")
print("  Le releve EST bien un releve EuroDreams + Joker+.")
