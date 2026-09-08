# Audit contradictoire — EuroDreams (Loterie Nationale, Belgique)

Re-calcul indépendant d'une analyse statistique portant sur 61 tirages joués
avec 4 grilles fixes + Joker+ (mise 11,50 €/tirage).

## Principe méthodologique

Toutes les probabilités de jeu sont **exactes** : le script énumère les
3 838 380 combinaisons de C(40,6) et calcule les lois par comptage, pas par
Monte-Carlo. Seuls les intervalles de confiance et la loi nulle du χ² utilisent
de la simulation.

## Scripts

| Fichier | Objet |
|---|---|
| `scripts/00_audit_complet_colab.py` | Script unique, copiable dans Google Colab |
| `scripts/01_probabilites_et_esperance.py` | Combinatoire des rangs, espérance nominale vs actualisée |
| `scripts/02_bilan_et_incertitude.py` | Bilan des 61 tirages, fenêtres, IC 95 %, tests de dérive |
| `scripts/03_couverture_grilles_exact.py` | Énumération exhaustive : couverture, P(≥1 gain), P(rentrer dans sa mise) |
| `scripts/04_chi2_loi_nulle_correcte.py` | Calibration du χ² pour un tirage sans remise + puissance |
| `scripts/05_joker_leviers_strategie.py` | Identification EuroDreams/Joker+, leviers, budget |
| `scripts/06_synthese_contradictoire.py` | Robustesse du « point 9 », choix de l'étalon |

```bash
pip install numpy scipy pandas
python scripts/00_audit_complet_colab.py
```

## Écarts principaux relevés par rapport à l'analyse auditée

1. **χ² mal calibré** : p = 0,22 et non 0,44 (les comptages issus d'un tirage
   sans remise sont négativement corrélés ; E[χ²] = 40(1−p) = 34, pas 39).
   Conclusion inchangée, chiffre faux. Puissance du test ≈ nulle.
2. **TRJ modèle** : 43,2 % avec la table de gains observée (44,1 % seulement si
   le rang 4 vaut 30 €). Actualisé à 3 %, la rente ramène le TRJ à 38,0 %.
   L'écart avec les 52 % annoncés n'est pas expliqué par la table supposée.
3. **IC 95 % du TRJ sur n = 61 : [22,4 % ; 47,0 %]**, soit 24,6 points de large.
   26,6 % et 43,2 % y sont tous deux. La « convergence vers 26,6 % » n'est pas
   soutenable ; il faudrait ~1 530 tirages pour un IC de 5 points.
4. **La décroissance du TRJ avec la fenêtre est un artefact de récence** :
   sur les fenêtres initiales, le TRJ *croît* (27,2 % → 33,1 %).
5. **P(rentrer dans sa mise) est robuste aux rangs 3 et 4** mais s'inverse dès
   que le rang 5 atteint 7,50 € : le phénomène tient au ratio rang 5 / rang 6.
6. **P(≥ 4 bons numéros) est exactement 4 × P(1 grille)** — démonstration :
   deux grilles ayant ≤ 1 numéro commun ne peuvent pas avoir 4 bons chacune
   (il faudrait ≥ 7 numéros tirés).
7. **Étalon correct hors jackpot = 28,2 %**. Le joueur est au 92ᵉ percentile,
   donc au-dessus de la médiane du modèle, pas en dessous.
8. **21 gains sur 61 sont impossibles en EuroDreams seul** → le TRJ de 33,1 %
   est un TRJ de portefeuille. Part EuroDreams bornée à [0 % ; 32,0 %].
9. **Pas de rollover en EuroDreams** : aucune fenêtre à espérance positive
   n'existe jamais (il faudrait une rente de valeur actuelle 34,5 M€).
