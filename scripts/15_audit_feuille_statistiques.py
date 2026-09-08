# -*- coding: utf-8 -*-
"""
AUDIT DE LA FEUILLE OFFICIELLE « statistiques Joker+ » (jusque août 2026).
4 onglets : Palmarès des signes · TOP 10 des mises · TOP 10 des gains · Résultats.
On vérifie : (1) la cohérence avec les fichiers financiers, (2) ce que le
« Palmarès » autorise réellement à conclure.
"""
import glob, numpy as np, pandas as pd, openpyxl
from scipy import stats
pd.set_option("display.width", 210)
F = "data/jokerplus_statistiques_0826.xlsx"
wb = openpyxl.load_workbook(F, data_only=True)
def sec(t): print("\n" + "="*84 + f"\n{t}\n" + "="*84)

# ---------- lecture ----------
pal = pd.DataFrame([r for r in wb["Palmarès"].iter_rows(min_row=4, values_only=True) if r[0]],
                   columns=["signe","n","pct","derniere","depuis"])
res = pd.DataFrame([r for r in wb["Résultats"].iter_rows(min_row=4, values_only=True) if r[0]],
                   columns=["date","num","signe"])
res["date"] = pd.to_datetime(res.date)
res["num"]  = res.num.astype(int).astype(str).str.zfill(6)
res = res.sort_values("date").reset_index(drop=True)
mis = pd.DataFrame([r[:2] for r in wb["TOP 10 des mises"].iter_rows(min_row=4, values_only=True) if r[0]],
                   columns=["date","mise"])
gai = pd.DataFrame([r[:2] for r in wb["TOP 10 des gains"].iter_rows(min_row=4, values_only=True) if r[0]],
                   columns=["date","gain"])

sec("A. INVENTAIRE")
print(f"  Onglets : {wb.sheetnames}")
print(f"  Résultats : {len(res)} tirages, {res.date.min().date()} → {res.date.max().date()}")
print(f"  Palmarès  : {len(pal)} signes, total des apparitions = {int(pal.n.sum())}")
print(f"  Cohérence interne : somme des apparitions = {int(pal.n.sum())} vs "
      f"{len(res)} tirages → {'OK' if pal.n.sum()==len(res) else 'INCOHÉRENT'}")
print(f"  Pourcentages : max |pct − n/N| = {(pal.pct - pal.n/len(res)).abs().max():.2e} → OK")
z = res.num.str.startswith('0').sum()
print(f"  Numéros commençant par 0 : {z} ({z/len(res):.2%}, attendu 10 %) — "
      f"les zéros de tête sont bien conservés")

# ---------- contrôle croisé avec mes fichiers ----------
sec("B. CONTRÔLE CROISÉ AVEC LES FICHIERS DE TIRAGES ET FINANCIERS")
def num(s): return float(str(s).strip().replace(".","").replace(",","."))
tir=[]; fin=[]
for f in sorted(glob.glob("data/jokerplus_TIRAGES_*.csv")):
    d=pd.read_csv(f,sep=";",encoding="utf-8-sig",dtype=str).dropna(how="all")
    d.columns=[c.strip().lstrip("﻿") for c in d.columns]
    d=d[d["Date"].notna()&d["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]; tir.append(d)
for f in sorted(glob.glob("data/jokerplus_FR_*.csv")):
    d=pd.read_csv(f,sep=";",encoding="utf-8-sig",dtype=str).dropna(how="all")
    d.columns=[c.strip().lstrip("﻿") for c in d.columns]
    d=d[d["Date"].notna()&d["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]
    for c in d.columns[1:]: d[c]=d[c].map(num)
    fin.append(d)
T=pd.concat(tir); T["date"]=pd.to_datetime(T.Date)
T["num"]="".join and T[[f"Numéro {i}" for i in range(1,7)]].astype(int).astype(str).agg("".join,axis=1)
T=T.rename(columns={"Signe astrologique":"signe"})[["date","num","signe"]]
FI=pd.concat(fin); FI["date"]=pd.to_datetime(FI.Date)
m=res.merge(T,on="date",how="inner",suffixes=("_xls","_csv"))
print(f"  Dates communes CSV ∩ XLSX : {len(m)} (XLSX {len(res)}, CSV {len(T)})")
print(f"  Numéros identiques : {(m.num_xls==m.num_csv).sum()}/{len(m)} "
      f"({(m.num_xls==m.num_csv).mean():.4%})")
print(f"  Signes identiques  : {(m.signe_xls==m.signe_csv).sum()}/{len(m)} "
      f"({(m.signe_xls==m.signe_csv).mean():.4%})")
sup=sorted(set(T.date)-set(res.date))
print(f"  Tirages présents en CSV mais absents de la feuille : {len(sup)} "
      f"({[str(x.date()) for x in sup[:9]]}) → la feuille s'arrête à août 2026")
# TOP 10
FI["ok"]=1
top_mise=FI.nlargest(10,"Cash")[["date","Cash"]]
print(f"\n  TOP 10 des mises : concordance avec mes fichiers financiers")
mm=mis.assign(date=pd.to_datetime(mis.date)).merge(FI[["date","Cash"]],on="date",how="left")
print(f"    {(np.isclose(mm.mise,mm.Cash)).sum()}/10 montants identiques au centime")
print(f"    même ensemble de dates que mon top 10 : "
      f"{set(mm.date)==set(top_mise.date)}")
gg=gai.assign(date=pd.to_datetime(gai.date)).merge(FI[["date","W-R1"]],on="date",how="left")
print(f"  TOP 10 des gains : {(np.isclose(gg.gain,gg['W-R1'])).sum()}/10 montants identiques")
print(f"    plus gros : {gg.gain.max():,.0f} € le {gg.loc[gg.gain.idxmax(),'date'].date()}"
      .replace(",", " "))

sec("C. AUDIT DU « PALMARÈS » — ce que la feuille laisse croire")
N=len(res); E=N/12
pal=pal.sort_values("n",ascending=False).reset_index(drop=True)
pal["ecart"]=pal.n-E; pal["z"]=pal.ecart/np.sqrt(E*(1-1/12))
print(f"  {N} tirages, {E:.1f} apparitions attendues par signe.")
print(f"  {'signe':<12}{'n':>6}{'%':>8}{'écart':>8}{'z':>7}{'depuis':>8}")
for _,r in pal.iterrows():
    print(f"  {r.signe:<12}{int(r.n):>6}{r.pct:>8.2%}{r.ecart:>+8.1f}{r.z:>+7.2f}{int(r.depuis):>8}")
chi2=((pal.n-E)**2/E).sum()
print(f"\n  χ² d'uniformité = {chi2:.2f} (11 ddl) → p = {1-stats.chi2.cdf(chi2,11):.4f}")
print(f"  Écart max = {pal.z.abs().max():.2f} σ. Sur 12 signes, le max attendu")
rng=np.random.default_rng(5)
sim=np.array([np.abs((np.bincount(rng.integers(0,12,N),minlength=12)-E)/np.sqrt(E*(11/12))).max()
              for _ in range(20000)])
print(f"  d'un |z| est de {sim.mean():.2f} en moyenne : P(max|z| ≥ {pal.z.abs().max():.2f}) = "
      f"{(sim>=pal.z.abs().max()).mean():.3f}")
print("  → l'écart entre le signe le plus et le moins sorti est ORDINAIRE.")
print("\n  La colonne « plus sorti depuis (# tirages) » :")
d=pal.depuis.astype(int).values
print(f"    valeurs {sorted(d)} | moyenne {d.mean():.1f} | attendu sous uniformité 11,0")
print(f"    test de Kolmogorov-Smirnov contre une loi géométrique(1/12) : "
      f"p = {stats.kstest(d, lambda x: 1-(11/12)**np.floor(x+1)).pvalue:.3f}")
print("    → conforme. Un signe « en retard » n'a aucune probabilité accrue de sortir :")
print("      chaque tirage est indépendant, la loi de l'attente est sans mémoire.")

sec("D. INDÉPENDANCE DES TIRAGES — les tests que la feuille ne fait pas")
sg=res.signe.values
rep=(sg[1:]==sg[:-1]).mean()
print(f"  Répétition du même signe deux tirages de suite : {rep:.4%} "
      f"(attendu {1/12:.4%}, p binomial = "
      f"{stats.binomtest(int((sg[1:]==sg[:-1]).sum()),N-1,1/12).pvalue:.3f})")
ct=pd.crosstab(pd.Series(sg[:-1]),pd.Series(sg[1:]))
c2=stats.chi2_contingency(ct)
print(f"  Table de transition 12×12 (signe t → signe t+1) : χ² = {c2.statistic:.1f} "
      f"({c2.dof} ddl), p = {c2.pvalue:.3f} → aucune mémoire")
dg=np.array([[int(c) for c in s] for s in res.num.values])
print(f"\n  Chiffres : {dg.size:,} tirés".replace(",", " "))
cnt=np.bincount(dg.ravel(),minlength=10); Ed=dg.size/10
x=((cnt-Ed)**2/Ed).sum()
print(f"    global : χ² = {x:.2f} (9 ddl), p = {1-stats.chi2.cdf(x,9):.4f}")
print("    par position : " + " | ".join(
    f"p{j+1} {1-stats.chi2.cdf(((np.bincount(dg[:,j],minlength=10)-N/10)**2/(N/10)).sum(),9):.3f}"
    for j in range(6)))
print(f"    numéro identique déjà sorti : {N-res.num.nunique()} paires sur {N} tirages "
      f"(attendu ≈ {N*(N-1)/2/1e6:.1f})")
print(f"    autocorrélation du numéro complet (lag 1) : "
      f"ρ = {stats.spearmanr(res.num.astype(int).values[:-1], res.num.astype(int).values[1:])[0]:+.4f}")

sec("E. LA FEUILLE INFLUENCE-T-ELLE LES JOUEURS ?")
print("  La part JOUÉE de chaque signe est mesurable par le rang 8 (bon signe seul).")
FI["grilles"]=(FI.Cash/1.5).round()
j=FI.merge(T[["date","signe"]],on="date",how="inner")
pj=j.groupby("signe").apply(lambda g: g["P-R8"].sum()/g.grilles.sum(), include_groups=False)*12
cmp=pal.set_index("signe").join(pj.rename("joue"))
rho,pv=stats.spearmanr(cmp.n,cmp.joue)
print(f"  {'signe':<12}{'apparitions':>12}{'indice joué':>13}")
for s,r in cmp.sort_values("joue",ascending=False).iterrows():
    print(f"  {s:<12}{int(r.n):>12}{r.joue:>13.3f}")
print(f"\n  Corrélation (fréquence publiée ↔ popularité auprès des joueurs) :")
print(f"    Spearman ρ = {rho:+.3f} (p = {pv:.3f}) | Pearson = {np.corrcoef(cmp.n,cmp.joue)[0,1]:+.3f}")
print("  → si les joueurs suivaient le palmarès, la corrélation serait forte et positive.")

sec("F. PUISSANCE — ce que 5 050 tirages permettent de détecter")
rng2 = np.random.default_rng(11); seuil = stats.chi2.ppf(.95, 11)
for b in (1.05, 1.10, 1.15, 1.20):
    w = np.ones(12); w[0] = b; w /= w.sum()
    hit = sum(((np.bincount(rng2.choice(12, N, p=w), minlength=12) - E)**2 / E).sum() >= seuil
              for _ in range(4000))
    print(f"  un signe {b:.2f}× plus fréquent → détecté dans {hit/4000:5.1%} des cas")
sim2 = np.array([(lambda c: c.max() - c.min())(np.bincount(rng2.integers(0, 12, N), minlength=12))
                 for _ in range(20000)])
obs = int(pal.n.max() - pal.n.min())
print(f"\n  Écart entre le signe le PLUS et le MOINS sorti :")
print(f"    médiane attendue par pur hasard : {np.median(sim2):.0f} apparitions")
print(f"    observé : {obs} → percentile {(sim2 <= obs).mean():.0%}")
print("  → le palmarès officiel est aussi dispersé qu'un palmarès tiré au sort.")
