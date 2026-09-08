# -*- coding: utf-8 -*-
"""
Prépare les données chiffrées de l'onglet « Popularité » de l'application v5.

Trois résultats, tous MESURÉS :
  1. la borne du levier anti-partage sur EuroDreams (déciles de fréquentation) ;
  2. la sur-dispersion Var(z) par rang — preuve que les joueurs cochent ;
  3. signes du zodiaque : fréquence publiée par la Loterie vs part réellement jouée.
Sortie : out/v5_popularite.json (embarqué en dur dans eurodreams_v5.html).
"""
import glob, json, numpy as np, pandas as pd, openpyxl
from scipy import stats

R = range(1, 7)
P = {1:1/19191900, 2:4/19191900, 3:204/3838380, 4:8415/3838380,
     5:119680/3838380, 6:695640/3838380}
NOM = {3:"Rang 3 — 5 n°", 4:"Rang 4 — 4 n°", 5:"Rang 5 — 3 n°", 6:"Rang 6 — 2 n°"}
def sec(t): print("\n" + "="*84 + f"\n{t}\n" + "="*84)

def charge(motif, cols_num=True):
    out = []
    for f in sorted(glob.glob(motif)):
        d = pd.read_csv(f, sep=";", encoding="utf-8-sig", dtype=str).dropna(how="all")
        d.columns = [c.strip().lstrip("﻿") for c in d.columns]
        d = d[d["Date"].notna() & d["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]
        if cols_num:
            for c in d.columns[1:]:
                d[c] = d[c].map(lambda s: float(str(s).strip().replace(".","").replace(",","."))
                                if not str(s).replace('.','',1).replace('-','',1).isdigit()
                                else float(s))
        out.append(d)
    return pd.concat(out).reset_index(drop=True)

ED = charge("data/eurodreams_FR_*.csv")
ED["Date"] = pd.to_datetime(ED.Date); ED = ED.sort_values("Date").reset_index(drop=True)
ED["grilles"] = (ED.Mise / 2.5).round()

# ============================================================================
sec("A. SUR-DISPERSION — les joueurs cochent-ils leurs numéros ?")
# Sous tirage au sort des grilles, k ~ B(n, p) et z = (k-np)/sqrt(np(1-p)) a Var = 1.
disp = []
for r in (3, 4, 5, 6):
    n = ED.grilles.to_numpy(float); k = ED[f"P-R{r}"].to_numpy(float); p = P[r]
    z = (k - n*p) / np.sqrt(n*p*(1-p))
    disp.append({"rang": r, "nom": NOM[r], "p": p,
                 "pobs": float((k/n).mean()), "var": float(z.var()),
                 "sd": float(np.sqrt(z.var())), "gag": int(k.sum())})
    print(f"  {NOM[r]:<16} Var(z) = {z.var():8.2f}  → écart-type ×{np.sqrt(z.var()):5.2f} "
          f"| {int(k.sum()):>10,} gagnants".replace(",", " "))
print("  Référence : Var(z) = 1 si les grilles étaient tirées au sort.")
print("  Joker+ (numéros NON choisis, 642 M de grilles) : Var(z) = 2,20 au rang 7.")

# ============================================================================
sec("B. BORNE DU LEVIER ANTI-PARTAGE — déciles de fréquentation")
# Espérance de gain d'UNE grille sur un tirage donné, rangs parimutuels 3-6 :
#   E = Σ p_r × W_r(tirage).  Les p_r sont fixes, seuls les lots bougent.
# On classe les 297 tirages par « encombrement » (z du rang 6, le plus informatif)
# et on regarde ce que vaut une grille selon le décile où elle tombe.
n = ED.grilles.to_numpy(float)
z6 = (ED["P-R6"].to_numpy(float) - n*P[6]) / np.sqrt(n*P[6]*(1-P[6]))
ev = sum(P[r] * ED[f"W-R{r}"].to_numpy(float) for r in (3,4,5,6))   # € par grille
ED2 = pd.DataFrame({"z6": z6, "ev": ev, "trj": ev/2.5})
ED2["dec"] = pd.qcut(ED2.z6, 10, labels=False)
g = ED2.groupby("dec").agg(n=("trj","size"), z=("z6","mean"), trj=("trj","mean"))
moy = ED2.trj.mean()
print(f"  TRJ moyen des rangs 3-6, tous tirages : {moy:.4%}")
print(f"\n  {'décile':<8}{'tirages':>8}{'z rang 6':>10}{'TRJ 3-6':>10}{'écart':>9}")
for d, r in g.iterrows():
    print(f"  D{int(d)+1:<7}{int(r.n):>8}{r.z:>+10.2f}{r.trj:>10.2%}{100*(r.trj-moy):>+8.2f} pt")
bas, haut = g.trj.iloc[0], g.trj.iloc[-1]
# décile le moins encombré = z le plus bas (moins de gagnants que prévu → lots plus gros)
d_best = g.trj.idxmax(); gain = g.trj.max() - moy
print(f"\n  Décile le plus rentable : D{int(d_best)+1} → {g.trj.max():.4%} "
      f"soit {100*gain:+.2f} point de TRJ")
print(f"  Amplitude D1 ↔ D10 : {100*abs(haut-bas):.2f} point")
print("  → BORNE SUPÉRIEURE du levier anti-partage : il faudrait tomber À COUP SÛR")
print("    dans le décile le moins fréquenté de chaque tirage, ce qui est impossible")
print("    (l'encombrement dépend du tirage, pas de la grille). Le levier réel est")
print("    une fraction de cette borne.")

# ============================================================================
sec("C. SIGNES DU ZODIAQUE — fréquence publiée vs part jouée (Joker+)")
wb = openpyxl.load_workbook("data/jokerplus_statistiques_0826.xlsx", data_only=True)
pal = pd.DataFrame([r for r in wb["Palmarès"].iter_rows(min_row=4, values_only=True) if r[0]],
                   columns=["signe","n","pct","derniere","depuis"])
res = pd.DataFrame([r for r in wb["Résultats"].iter_rows(min_row=4, values_only=True) if r[0]],
                   columns=["date","num","signe"])
res["date"] = pd.to_datetime(res.date)

FI = charge("data/jokerplus_FR_*.csv")
FI["date"] = pd.to_datetime(FI.Date); FI["grilles"] = (FI.Cash/1.5).round()
T = charge("data/jokerplus_TIRAGES_*.csv", cols_num=False)
T["date"] = pd.to_datetime(T.Date); T = T.rename(columns={"Signe astrologique":"signe"})
j = FI.merge(T[["date","signe"]], on="date", how="inner")
# rang 8 = bon signe seul : sa fréquence de gain mesure la part JOUÉE du signe
pj = j.groupby("signe").apply(lambda g: g["P-R8"].sum()/g.grilles.sum(),
                              include_groups=False) * 12
cmp = pal.set_index("signe").join(pj.rename("joue")).sort_values("joue", ascending=False)
N = len(res); E = N/12
cmp["z"] = (cmp.n - E) / np.sqrt(E*(1-1/12))
rho, pv = stats.spearmanr(cmp.n, cmp.joue)
print(f"  {'signe':<12}{'sorti':>7}{'z':>7}{'indice joué':>13}")
for s, r in cmp.iterrows():
    print(f"  {s:<12}{int(r.n):>7}{r.z:>+7.2f}{r.joue:>13.3f}")
print(f"\n  Spearman ρ(sorti, joué) = {rho:+.3f} (p = {pv:.3f})")
print(f"  Amplitude de la popularité : ×{cmp.joue.max()/cmp.joue.min():.3f}")
print("  → les joueurs NE suivent PAS le palmarès officiel. La popularité d'un")
print("    signe est culturelle, pas statistique : c'est ce qui rend le levier")
print("    exploitable — il faut jouer ce que les autres ne jouent pas.")
# Valeur du levier, telle que mesurée dans scripts/10_popularite_mesuree.py :
# dans le Joker+ SEUL le rang 1 est partagé (rangs 2 à 8 = montants fixes).
# Choisir le signe le moins joué divise le nombre de co-gagnants attendus par
# 1,213 → +0,436 point de TRJ ; en y ajoutant les deux extrémités de chiffres
# (×1,02 et ×1,01) le ratio monte à ~1,26 → +0,572 point au mieux.
LEVIER_JK = {"min": 0.00436, "max": 0.00572, "ratioSigne": float(cmp.joue.max()/cmp.joue.min())}
print(f"\n  Valeur du levier (mesurée en 10_popularite_mesuree.py) : "
      f"+0,436 pt (signe seul) à +0,572 pt (signe + chiffres).")
print("  Dans le Joker+ seul le rang 1 est partagé : les rangs 2 à 8 sont à")
print("  montants fixes, la popularité n'y change rien.")

OUT = {
  "disp": disp,
  "dec": [{"d": int(d)+1, "n": int(r.n), "z": float(r.z), "trj": float(r.trj)}
          for d, r in g.iterrows()],
  "trjMoy": float(moy), "trjMax": float(g.trj.max()), "gain": float(gain),
  "signes": [{"s": s, "n": int(r.n), "z": float(r.z), "joue": float(r.joue)}
             for s, r in cmp.iterrows()],
  "rho": float(rho), "rhoP": float(pv), "nJk": int(N), "levierJk": LEVIER_JK,
  "nED": int(len(ED)), "grillesED": int(ED.grilles.sum())
}
with open("out/v5_popularite.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False)
print("\n→ out/v5_popularite.json")
