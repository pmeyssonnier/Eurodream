# -*- coding: utf-8 -*-
"""
EuroDreams - AUDIT 1/4 : probabilites par rang (combinatoire exacte)
                          et esperance mathematique (nominale vs actualisee).
Colab-ready : aucune dependance externe hors numpy/pandas.
"""
from math import comb
from fractions import Fraction
import pandas as pd

# ----------------------------------------------------------------------
# 1. Structure du jeu
# ----------------------------------------------------------------------
N, K, D = 40, 6, 5                 # 6 numeros parmi 40, 1 Dream parmi 5
C_NUM   = comb(N, K)               # 3 838 380
C_TOT   = C_NUM * D                # 19 191 900
print(f"C(40,6) = {C_NUM:,}".replace(",", " "))
print(f"C(40,6) x 5 = {C_TOT:,}".replace(",", " "))

# ----------------------------------------------------------------------
# 2. Nombre de tirages favorables par rang, calcul exact
#    (la loi est hypergeometrique : C(6,m) * C(34, 6-m))
# ----------------------------------------------------------------------
def favorables(m):
    """Nombre de tirages de 6 numeros parmi 40 ayant exactement m numeros communs
    avec une grille donnee."""
    return comb(K, m) * comb(N - K, K - m)

hyp = {m: favorables(m) for m in range(K + 1)}
assert sum(hyp.values()) == C_NUM, "la loi hypergeometrique doit sommer a C(40,6)"

# Le Dream ne discrimine QUE le rang 1 vs le rang 2 (6 numeros).
rangs = [
    ("Rang 1", "6 + Dream", hyp[6] * 1,            C_TOT),
    ("Rang 2", "6",         hyp[6] * (D - 1),      C_TOT),
    ("Rang 3", "5",         hyp[5],                C_NUM),
    ("Rang 4", "4",         hyp[4],                C_NUM),
    ("Rang 5", "3",         hyp[3],                C_NUM),
    ("Rang 6", "2",         hyp[2],                C_NUM),
]

rows = []
for nom, cond, fav, denom in rangs:
    p = Fraction(fav, denom)
    rows.append(dict(rang=nom, condition=cond, favorables=fav, denominateur=denom,
                     p=float(p), un_sur=1 / float(p)))
df = pd.DataFrame(rows)
print("\n--- Probabilites exactes par rang ---")
print(df.to_string(index=False,
                   formatters={"p": "{:.3e}".format, "un_sur": "{:,.1f}".format}))

p_gain = sum(r["p"] for r in rows)
print(f"\nP(gain quelconque, 1 grille) = {p_gain:.6f}  (1 sur {1/p_gain:.3f})")
print(f"P(aucun gain,     1 grille) = {1-p_gain:.6f}")
print(f"Controle hypergeometrique  : P(>=2 bons) = "
      f"{sum(hyp[m] for m in (2,3,4,5,6))/C_NUM:.6f}")

# ----------------------------------------------------------------------
# 3. Esperance : deux tables de gains, deux valorisations de la rente
# ----------------------------------------------------------------------
def pv_rente(mensualite, annees, taux_annuel):
    """Valeur actuelle d'une rente mensuelle constante (paiements en fin de mois)."""
    if taux_annuel == 0:
        return mensualite * 12 * annees
    r = taux_annuel / 12.0
    n = int(round(12 * annees))
    return mensualite * (1 - (1 + r) ** (-n)) / r

TABLES = {
    # table "audit joueur" : rang 3 = 500, rang 4 = 30
    "joueur":  {"Rang 3": 500.0, "Rang 4": 30.0, "Rang 5": 5.0, "Rang 6": 2.50},
    # table "observee"    : rang 4 = 20 (montant reellement constate)
    "observee":{"Rang 3": 500.0, "Rang 4": 20.0, "Rang 5": 5.0, "Rang 6": 2.50},
    # table "basse"       : hypothese parimutuel degrade
    "basse":   {"Rang 3": 300.0, "Rang 4": 15.0, "Rang 5": 4.0, "Rang 6": 2.50},
}
MISE = 2.50

print("\n--- Esperance par grille de 2,50 EUR ---")
res = []
for taux in (0.0, 0.02, 0.03):
    r1 = pv_rente(20000, 30, taux)
    r2 = pv_rente(2000, 5, taux)
    for nom_table, tbl in TABLES.items():
        ev = 0.0
        detail = {}
        for row in rows:
            gain = {"Rang 1": r1, "Rang 2": r2}.get(row["rang"], tbl.get(row["rang"], 0.0))
            detail[row["rang"]] = row["p"] * gain
            ev += row["p"] * gain
        res.append(dict(taux_actu=taux, table=nom_table, VA_rang1=r1, VA_rang2=r2,
                        EV=ev, TRJ=ev / MISE, **{f"c_{k}": v for k, v in detail.items()}))
ev_df = pd.DataFrame(res)
print(ev_df[["taux_actu", "table", "VA_rang1", "EV", "TRJ"]].to_string(
    index=False, formatters={"VA_rang1": "{:,.0f}".format, "EV": "{:.4f}".format,
                             "TRJ": "{:.2%}".format, "taux_actu": "{:.0%}".format}))

print("\n--- Decomposition de l'esperance (table 'observee', rente nominale) ---")
ref = ev_df[(ev_df.table == "observee") & (ev_df.taux_actu == 0.0)].iloc[0]
tot = ref["EV"]
for row in rows:
    c = ref[f"c_{row['rang']}"]
    print(f"  {row['rang']} ({row['condition']:>9}) : {c:.4f} EUR  "
          f"= {c/tot:6.2%} de l'esperance  ({c/MISE:6.2%} de la mise)")
print(f"  TOTAL                : {tot:.4f} EUR = {tot/MISE:.2%} de la mise")

# ----------------------------------------------------------------------
# 4. Reverse-engineering : quel gain rang 3 faudrait-il pour atteindre 52 % ?
# ----------------------------------------------------------------------
cible = 0.52 * MISE
base = sum(r["p"] * ({"Rang 1": pv_rente(20000, 30, 0), "Rang 2": pv_rente(2000, 5, 0)}
                     .get(r["rang"], TABLES["observee"].get(r["rang"], 0.0)))
           for r in rows if r["rang"] != "Rang 3")
p3 = next(r["p"] for r in rows if r["rang"] == "Rang 3")
print(f"\nPour un TRJ affiche de 52 % avec le reste de la table 'observee' (rente nominale),")
print(f"il faudrait un rang 3 a {(cible-base)/p3:,.0f} EUR "
      f"(vs 500 EUR suppose) -> l'ecart de TRJ ne peut PAS venir du seul rang 3.")
