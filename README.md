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

## Complément — le TRJ réel du Joker+ (données officielles 2011-2026)

16 fichiers de données financières (5 057 tirages, 963,2 M€ misés, 642,1 M grilles
à 1,50 €) permettent de mesurer directement le TRJ du Joker+ :

| | TRJ moyen | TRJ hors jackpot | P(gain)/grille |
|---|---|---|---|
| EuroDreams (2,50 €) | 43,18 % | 28,18 % | 21,47 % |
| **Joker+ (1,50 €)** | **52,39 %** | **46,80 %** | **26,67 %** |

Écart-type du TRJ hors jackpot du Joker+ entre les 16 années : **0,175 point**.

Conséquences :
1. **Abandonner le Joker+ est la pire décision du portefeuille** : c'est la ligne
   la mieux rémunérée. Hors jackpot le Joker+ rend 1,66 fois plus par euro.
2. Le **52 % annoncé** est atteint par le Joker+ (52,39 %) et non par EuroDreams
   (43,18 %) — l'écart de 9 points relevé dans l'audit se situe sur EuroDreams.
3. **Le jackpot Joker+ roule** (200 000 € → 3 125 000 € observés, 56 gains en
   16 ans, partagés) : le TRJ passe de 48,0 % à 65,3 % selon la cagnotte. Le
   levier « jackpot roulé » existe donc — mais dans le Joker+, pas dans EuroDreams.
   Seuil d'espérance nulle : 8,99 M€, soit 2,9 fois le maximum jamais atteint.
4. Structure reconstituée par les fréquences : 6 chiffres alignés par **l'une des
   deux extrémités** + 1 signe du zodiaque parmi 12, dont le lot **se cumule**
   (p(R8) = 1/12 exactement ; p(Rk) = 2 × 0,9 × 10⁻ᵏ ; p(R1) = 1 sur 11,3 M).
5. **Validation du modèle complet** : P(gain nul sur un tirage) prédite 27,59 %,
   observée 17/61 = 27,87 % (test binomial p = 1,000).
6. **Anomalie de calendrier** : 60 des 61 dates du joueur tombent un mardi ou un
   vendredi ; EuroDreams est tiré le lundi et le jeudi. À élucider.

## Complément 2 — les tirages Joker+ (2011-2026) : uniformité et popularité

16 fichiers de résultats (5 057 tirages : 6 chiffres + 1 signe du zodiaque),
appariés aux données financières.

**Le générateur est uniforme.** 30 342 chiffres tirés : χ² = 5,70 (9 ddl),
p = 0,77 ; aucune position biaisée ; signes tirés χ² = 14,88 (11 ddl), p = 0,19.
Ici le χ² classique est **valide** (tirage avec remise, chiffres indépendants),
contrairement au cas EuroDreams. Puissance : un chiffre 10 % plus fréquent serait
détecté dans **97 %** des cas, contre 5,5 % avec les 297 tirages EuroDreams.

**Les grilles jouées, elles, ne sont pas uniformes.** Les comptages de gagnants
sont sur-dispersés (Var(z) = 2,20 au rang 7 et 33,5 au rang 8, au lieu de 1),
ce qui permet de reconstituer la distribution des grilles jouées sans y avoir accès :

| dimension | amplitude max/min | le plus joué | le moins joué |
|---|---|---|---|
| Signe du zodiaque | **1,213×** | Lion (indice 1,110) | Capricorne (0,916) |
| Chiffre, 1ʳᵉ position | 1,022× | 7 | 0 (z = −19,3) |
| Chiffre, 6ᵉ position | 1,013× | 7 | 0 (z = −9,0) |

Préférence **stable** sur 15 ans (Spearman entre 2011-2018 et 2019-2026 : ρ = +0,94).

**Valeur du levier anti-partage, enfin chiffrée.** Seul le rang 1 du Joker+ est
partagé (rangs 2 à 8 : montants fixes). Jouer le profil le moins populaire plutôt
que le plus populaire vaut au mieux **+0,44 à +0,57 point de TRJ**, contre 46,80 %
de TRJ hors jackpot. La conclusion A de l'audit est donc **validée empiriquement
pour la première fois — et simultanément réduite à une quantité négligeable.**
