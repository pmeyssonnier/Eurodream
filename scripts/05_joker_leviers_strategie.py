# -*- coding: utf-8 -*-
"""
EuroDreams - AUDIT 5 : (a) le probleme d'identification EuroDreams / Joker+,
(b) les leviers reellement disponibles, chiffres.
"""
import itertools, numpy as np, pandas as pd
from math import comb

N, K = 40, 6; C = comb(N, K)
GAINS = np.array([7.0,0,2.0,2.5,4.0,4.5,0,5.0,0,0,2.5,4.5,2.5,0,2.5,2.5,2.5,1.5,2.5,0,
                  0,6.5,7.3,11.7,7.0,1.5,4.0,0,4.5,7.5,2.5,2.0,0,0,2.5,2.5,9.0,2.5,0,0,
                  0,4.0,7.5,0,0,5.5,2.5,2.5,2.5,0,10.4,2.5,5.0,38.5,2.5,20.0,2.5,2.0,0,2.0,5.0])
n = len(GAINS); MISE_TOT, MISE_ED, MISE_JK = 11.50, 10.00, 1.50
assert n == 61 and abs(GAINS.sum() - 231.90) < 1e-9

# ======================================================================
# A. IDENTIFICATION : quelle part vient d'EuroDreams ?
# ======================================================================
print("="*78); print("A. Decomposition EuroDreams / Joker+ : ce qui est identifiable"); print("="*78)

# Totaux EuroDreams atteignables avec 4 grilles : a*2.50 + b*5 + c*20 + d*500,
# a+b+c+d <= 4 (une grille = un seul rang)
atteignables = set()
for a in range(5):
    for b in range(5-a):
        for c in range(5-a-b):
            for d in range(5-a-b-c):
                atteignables.add(round(2.5*a + 5*b + 20*c + 500*d, 2))
atteignables = sorted(x for x in atteignables if x <= 60)
print(f"Totaux EuroDreams possibles (<=60 EUR, 4 grilles) : {atteignables}")

mult = np.array([g in atteignables for g in GAINS])
print(f"\nTirages dont le gain est compatible avec 'EuroDreams seul' : {mult.sum()}/{n}")
print(f"Tirages OBLIGATOIREMENT contamines par le Joker+          : {(~mult).sum()}/{n}"
      f"  -> {sorted(set(GAINS[~mult]))}")
ed_max = np.array([max([a for a in atteignables if a <= g], default=0.0) for g in GAINS])
print(f"\nBorne SUPERIEURE de la part EuroDreams : {ed_max.sum():.2f} EUR "
      f"-> TRJ_ED <= {ed_max.sum()/(n*MISE_ED):.2%}")
print(f"Borne INFERIEURE (tout au Joker+)      : 0.00 EUR -> TRJ_ED >= 0 %")
print("-> l'historique agrege NE PERMET PAS d'estimer le TRJ EuroDreams seul.")
print("   Tout chiffre 'TRJ EuroDreams = 33 %' est un TRJ de PORTEFEUILLE, pas du jeu.")

# Estimateur des moments du taux de reussite Joker+ via la frequence de zeros
P_ED_ZERO = 1 - 0.623792                      # exact, script 03
p0_obs = (GAINS == 0).mean()
p_jk_win = 1 - p0_obs / P_ED_ZERO
k0 = int((GAINS == 0).sum())
from scipy import stats as st
lo0, hi0 = st.beta.ppf([.025, .975], k0, n-k0+1)[0], st.beta.ppf([.025, .975], k0+1, n-k0)[1]
print(f"\nEstimateur par les zeros :")
print(f"  P(gain nul) observe        = {p0_obs:.4f}  ({k0}/{n}, IC95 Clopper-Pearson [{lo0:.3f} ; {hi0:.3f}])")
print(f"  P(aucun gain EuroDreams)   = {P_ED_ZERO:.4f} (exact)")
print(f"  => P(gain Joker+) estime   = {p_jk_win:.3f}  "
      f"IC95 ~ [{max(0,1-hi0/P_ED_ZERO):.3f} ; {1-lo0/P_ED_ZERO:.3f}]")
print("  Le Joker+ gagne donc environ 1 tirage sur 4 : ce n'est PAS un poste negligeable.")

# Esperance EuroDreams theorique sur la periode
EV_G = 1.0796
print(f"\nGain EuroDreams ESPERE sur {n} tirages x 4 grilles : {n*4*EV_G:.2f} EUR")
print(f"Gain TOTAL observe (EuroDreams + Joker+)          : {GAINS.sum():.2f} EUR")
print(f"-> le total encaisse est INFERIEUR a l'esperance EuroDreams seule.")
print("   (mais l'esperance est portee a 35 % par le rang 1 : comparaison peu informative,")
print("    cf. esperance hors rang 1 ci-dessous)")
EV_G_hors_r1 = EV_G - 0.3752
print(f"Esperance hors rang 1 : {n*4*EV_G_hors_r1:.2f} EUR  vs  {GAINS.sum():.2f} observe "
      f"(ratio {GAINS.sum()/(n*4*EV_G_hors_r1):.2f})")

# ======================================================================
# B. LEVIERS
# ======================================================================
print("\n" + "="*78); print("B. Leviers : lesquels bougent l'esperance, de combien"); print("="*78)

# B1 - jackpot de rentabilite
p = {1: 1/19191900, 2: 4/19191900, 3: 204/C, 4: 8415/C, 5: 119680/C, 6: 695640/C}
ev_hors_r1 = p[2]*120000 + p[3]*500 + p[4]*20 + p[5]*5 + p[6]*2.5
seuil = (2.50 - ev_hors_r1) / p[1]
print(f"\nB1. Rollover / jackpot : pour que l'esperance atteigne la mise (2,50 EUR),")
print(f"    il faudrait un rang 1 d'une VALEUR ACTUELLE de {seuil:,.0f} EUR".replace(",", " "))
print(f"    = ~{seuil/(12*30):,.0f} EUR/mois pendant 30 ans (vs 20 000 EUR/mois)."
      .replace(",", " "))
print("    Le rang 1 EuroDreams est une RENTE FIXE, partagee s'il y a plusieurs")
print("    gagnants : il n'y a pas de rollover, donc AUCUNE fenetre a esperance")
print("    positive n'existe jamais. Le levier 'jackpot rouli' d'EuroMillions")
print("    n'existe pas ici. C'est un point que l'audit initial n'a pas releve.")

# B2 - anti-partage : quelle fraction de l'esperance est concernee ?
part_fixe = p[6]*2.5 / EV_G
print(f"\nB2. Anti-partage (jouer impopulaire) :")
print(f"    part de l'esperance venant du rang 6 a 2,50 EUR FIXE : {part_fixe:.1%}")
print(f"    -> au mieux {1-part_fixe:.0%} de l'esperance est exposee au partage.")
for boost in (0.10, 0.25, 0.50):
    ev2 = p[6]*2.5 + (1-part_fixe)*EV_G*(1+boost)
    print(f"    si l'evitement des combinaisons populaires majore de {boost:+.0%} les rangs "
          f"partages : TRJ {EV_G/2.5:.1%} -> {ev2/2.5:.1%}")
print("    Contradiction a lever : si le rang 6 est FIXE a 2,50 EUR, la premisse")
print("    'tous les rangs 3-6 sont parimutuels' est fausse, et le levier est plus")
print("    faible encore que ce que l'audit suppose.")

# B3 - popularite des grilles du joueur
JOUEUR = [(4,5,6,22,31,32),(5,8,16,18,19,34),(9,11,14,31,34,39),(3,16,27,29,32,37)]
flat = [x for g in JOUEUR for x in g]
print(f"\nB3. Les grilles du joueur sont-elles 'impopulaires' ? (proxys usuels)")
print(f"    numeros <= 31 (dates)        : {sum(x<=31 for x in flat)}/24 = "
      f"{sum(x<=31 for x in flat)/24:.0%}  (attendu au hasard {31/40:.0%})")
print(f"    numeros <= 12 (mois)         : {sum(x<=12 for x in flat)}/24 = "
      f"{sum(x<=12 for x in flat)/24:.0%}  (attendu {12/40:.0%})")
cons = sum(1 for g in JOUEUR for a,b in zip(sorted(g), sorted(g)[1:]) if b-a==1)
print(f"    paires consecutives          : {cons} (4-5, 5-6, 31-32 ...)")
print(f"    somme moyenne des grilles    : {np.mean([sum(g) for g in JOUEUR]):.1f} "
      f"(attendu {6*41/2:.1f})")
print("    -> profil globalement BANAL, voire legerement 'populaire' (suite 4-5-6,")
print("       forte densite de petits numeros dans G1). L'affirmation B de l'audit")
print("       ('un set fixe impopulaire verrouille l'avantage anti-partage') ne")
print("       s'applique pas a CE set : il n'est pas impopulaire.")

# B4 - syndicat / pool : effet exact sur la variance
print(f"\nB4. Syndicat (mise en commun) : l'esperance par euro est INCHANGEE.")
print("    Seul effet : reduction de la variance du rendement par euro mise.")
print("    Var(rendement) d'un pool de m joueurs ~ Var(1 joueur)/m.")
print("    Consequence contre-intuitive : cela RAPPROCHE le resultat de la perte")
print("    esperee, donc rend la perte plus CERTAINE. Un pool n'est utile que si")
print("    l'objectif est 'maximiser P(toucher un jour un gros lot)', pas 'perdre moins'.")

# B5 - Dream number
print(f"\nB5. Dream number : n'intervient QUE pour separer rang 1 et rang 2.")
print(f"    Esperance identique quel que soit le Dream choisi. Jouer 3 Dreams")
print(f"    distincts sur 4 grilles n'apporte ni ne coute rien en esperance ;")
print(f"    cela ne change que la repartition rang1/rang2 conditionnellement aux")
print(f"    6 bons numeros (proba 5,2e-8 par grille). Effet pratique : nul.")

# B6 - Joker+
print(f"\nB6. Joker+ : {MISE_JK:.2f} EUR/tirage = {MISE_JK/MISE_TOT:.1%} de la mise,")
print(f"    taux de reussite estime ~{p_jk_win:.0%}/tirage, TRJ INCONNU.")
print("    C'est le seul poste du portefeuille dont le rendement n'est pas")
print("    documente ici. Priorite d'audit n1 : recuperer la table officielle.")

# ======================================================================
# C. STRATEGIE SOUS CONTRAINTE DE BUDGET
# ======================================================================
print("\n" + "="*78); print("C. Budget annuel -> perte esperee (le seul cadrage valide)"); print("="*78)
tirages_an = n / ((pd.Timestamp("2026-07-03")-pd.Timestamp("2025-09-05")).days/365.25)
print(f"Rythme observe : {tirages_an:.1f} tirages/an (le joueur saute des tirages ;")
print(f"le calendrier officiel en compte ~104/an -> il ne joue que {tirages_an/104:.0%} des tirages).")
rows = []
for k in (0, 1, 2, 3, 4):
    for jk in (False, True):
        mise_t = 2.5*k + (1.5 if jk else 0)
        if mise_t == 0: 
            rows.append(dict(grilles=0, joker=False, mise_tirage=0, budget_an=0,
                             perte_esperee_an=0, TRJ="n/a")); continue
        ev_t = k*EV_G                      # Joker+ : rendement inconnu -> compte 0 (pire cas)
        rows.append(dict(grilles=k, joker=jk, mise_tirage=mise_t,
                         budget_an=mise_t*tirages_an,
                         perte_esperee_an=(mise_t-ev_t)*tirages_an,
                         TRJ=f"{ev_t/mise_t:.1%}"))
bud = pd.DataFrame(rows).drop_duplicates()
print(bud.to_string(index=False, formatters={"budget_an":"{:.0f} EUR".format,
                                             "perte_esperee_an":"{:.0f} EUR".format,
                                             "mise_tirage":"{:.2f}".format}))
print("\nNB : la colonne TRJ compte le Joker+ a 0 (rendement inconnu) : c'est une")
print("borne INFERIEURE. Si le Joker+ redistribue ~50 %, le TRJ 4 grilles+Joker")
print(f"passe de {4*EV_G/11.5:.1%} a {(4*EV_G+0.5*1.5)/11.5:.1%}.")
