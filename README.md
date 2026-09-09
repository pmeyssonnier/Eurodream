# EuroDreams + Joker+ — audit statistique contradictoire

Recalcul indépendant, à partir des données officielles de la Loterie Nationale, de
ce que rapportent réellement EuroDreams et le Joker+. Le projet a commencé comme
l'audit d'une analyse portant sur 61 tirages joués à 11,50 €, et s'est transformé en
reconstruction complète des deux jeux à partir de leurs règles.

**Toutes les probabilités de jeu sont exactes.** Les 3 838 380 combinaisons de C(40,6)
sont énumérées, la loi du gain Joker+ est dérivée du couple (chiffres alignés à gauche,
à droite). La simulation ne sert qu'aux lois nulles, aux puissances de test et aux
enveloppes de trajectoire.

---

## Résultats principaux

| Question | Réponse mesurée |
|---|---|
| TRJ d'EuroDreams, tirage ordinaire | **44,50 %** nominal · **39,35 %** rente actualisée à 3 % |
| TRJ d'EuroDreams, tirage **Boost** | **52,00 %** — exactement le chiffre annoncé |
| Où passent les 7,5 points d'écart | Fonds de Réserve : il met de côté **7,5024 %** par tirage ordinaire, un Boost coûte **7,5032 %** |
| TRJ du Joker+ | **52,39 %** versés sur 963 M€, dont **46,80 %** hors jackpot |
| Loi du Joker+ dérivée des règles | **46,7555 %** hors jackpot — 0,045 point de l'observé, sans un seul paramètre libre |
| Seuil d'espérance nulle du Joker+ | cagnotte de **9 584 002 €**, soit 3,8× le plafond actuel |
| Les joueurs choisissent-ils leurs numéros ? | EuroDreams **oui** : Var(z) = 54,22 au rang 6 contre 1 attendu. Joker+ **non** : les 6 chiffres sont attribués, seul le signe est choisi |
| Que vaut « éviter les combinaisons populaires » ? | Joker+, seul cas entièrement modélisable : **+0,005 point** de TRJ. EuroDreams : **non mesuré**, il manque les numéros tirés |
| Le palmarès officiel des signes dit-il quelque chose ? | Non : χ² = 14,79 (p = 0,19), écart max au 63ᵉ percentile du pur hasard |

**Le seul levier qui dépasse le dixième de point** est de jouer le Joker+ quand la
cagnotte est haute : +5,5556 points de TRJ par million d'euros de cagnotte, soit
jusqu'à +13,9 points au plafond actuel. Il reste très insuffisant pour rendre
l'espérance positive.

---

## Application

`eurodreams_v6.html` — un fichier, aucune dépendance, aucun réseau. Cinq onglets :
générateur de grilles, bankroll, données officielles, cagnotte Joker+, popularité.
Ouvrir le fichier dans un navigateur suffit.

Les versions antérieures sont conservées telles quelles comme références historiques :
`eurodreams_v3.html`, `eurodreams_v4.html`, `eurodreams_v5.html`.

---

## Tests

```bash
pip install numpy scipy pandas
python tests/run_all.py           # 41 tests, ~20 s
```

41 tests répartis en cinq modules, sans dépendance à pytest :

| Module | Ce qu'il garantit |
|---|---|
| `tests/test_probabilites.py` | Combinatoire exacte d'EuroDreams : effectifs hypergéométriques, somme des lois à 1, énumération exhaustive, P(≥1 gain) par nombre de grilles |
| `tests/test_joker_pmf.py` | La loi du Joker+ somme à 1, reproduit les 0,18 lot de rang 7 par grille **et** le « 1 sur 3,88 » officiel, donne le bon TRJ et le bon seuil |
| `tests/test_donnees.py` | Intégrité des CSV officiels, lots fixes, part de 28,44 % aux rangs 3-6, identité du Fonds de Réserve et du Boost, sur-dispersion |
| `tests/test_application.py` | **Les constantes du HTML correspondent aux calculs Python** — et `setJackpot()` est réellement exécuté dans node puis comparé à la loi exacte |
| `tests/test_navigateur.py` | Les cinq onglets se rendent sans erreur JavaScript ; le générateur plafonne les grilles disjointes ; la bankroll compte les tirages Boost (ignoré si Playwright est absent) |

La suite a été validée par mutation : fausser `P_R1_JK`, `PMISE_AVEC`, le plafond de
grilles disjointes ou un lot dans un CSV fait échouer les tests concernés. C'est le
module `test_application.py` qui a trouvé que le `<title>` de l'application était
resté en « v3 » pendant trois versions.

---

## Scripts

Ordre de lecture recommandé : 11 → 19. Les scripts 00 à 10 datent des premières
passes ; ceux marqués LEGACY portent un bandeau en tête de fichier.

| Fichier | Objet | État |
|---|---|---|
| `00_audit_complet_colab.py` | Script unique pour Colab, première passe | **LEGACY** — table de gains supposée |
| `01_probabilites_et_esperance.py` | Combinatoire des rangs, espérance nominale vs actualisée | valide |
| `02_bilan_et_incertitude.py` | Bilan des 61 tirages, fenêtres, dérive | valide, mais l'IC bootstrap est remplacé par le script 19 |
| `03_couverture_grilles_exact.py` | Énumération exhaustive : couverture, P(≥1 gain), P(rentrer dans sa mise) | valide |
| `04_chi2_loi_nulle_correcte.py` | Calibration du χ² sans remise + puissance | valide, puissance recalibrée en v6 |
| `05_joker_leviers_strategie.py` | Identification EuroDreams/Joker+, leviers, budget | valide, valorisation du levier remplacée par le 18 |
| `06_synthese_contradictoire.py` | Robustesse du « point 9 », choix de l'étalon | valide |
| `07_jokerplus_trj_reel.py` | TRJ Joker+ mesuré sur 2011-2026 | valide |
| `08_portefeuille_exact_avec_joker.py` | Loi exacte du portefeuille par convolution | valide, PMF remplacée par le 19 |
| `09_jokerplus_tirages_exploitabilite.py` | Uniformité du générateur Joker+ | **LEGACY** — la partie « signature humaine » est réfutée |
| `10_popularite_mesuree.py` | Popularité mesurée des signes et des chiffres | **LEGACY** — les chiffres ne sont pas choisis ; levier faux |
| `11_eurodreams_donnees_reelles.py` | 297 tirages officiels, table de gains réelle | valide |
| `12_identification_du_releve.py` | Le relevé du joueur correspond-il à EuroDreams ? | valide |
| `13_reconciliation_finale.py` | Réconciliation ligne à ligne des 61 tirages | valide |
| `14_analyse_financiere_eurodreams.py` | Parimutuel, sur-dispersion, changement d'octobre 2025 | valide |
| `15_audit_feuille_statistiques.py` | Audit du classeur officiel Joker+ | valide |
| `16_donnees_v5_popularite.py` | Données de l'onglet Popularité v5 | superseded par le 18 |
| `17_contre_audit_reglement.py` | Trois objections externes, testées contre les données | valide |
| `18_v6_modele_exact.py` | PMF Joker+ dérivée des règles, modèle de co-gagnants | valide |
| `19_v6_boost_et_pmf_exacte.py` | Fonds de Réserve, Boost, loi exacte (L, T), test des 61 tirages | valide |

```bash
pip install numpy scipy pandas openpyxl
python scripts/19_v6_boost_et_pmf_exacte.py
```

---

## Données

`data/` contient les fichiers publiés par la Loterie Nationale :
16 fichiers financiers Joker+ (2011-2026, 5 057 tirages, 963 M€ de mises),
16 fichiers de tirages Joker+ (numéros + signe), 4 fichiers financiers EuroDreams
(2023-2026, 297 tirages, 140,7 M€), et le classeur officiel de statistiques Joker+.

**Manquant** — les 297 combinaisons tirées d'EuroDreams (`eurodreams-gamedata-FR-*.csv`).
Sans elles, impossible de relier les caractéristiques d'une grille à son nombre attendu
de co-gagnants : le score d'impopularité du générateur reste une heuristique non
calibrée, et l'application le dit.

---

## Ce que le projet ne prétend pas

- Aucune combinaison n'a plus de chances de sortir qu'une autre. Les tests de RNG
  passent tous, et la puissance disponible est faible (6 % contre un biais de 10 %
  sur 297 tirages) : « aucun biais détecté » ne veut pas dire « tirage prouvé équitable ».
- Le générateur n'améliore pas votre probabilité de gagner. Il ne peut agir que sur le
  **partage** des lots parimutuels, dont l'ampleur reste à démontrer sur EuroDreams.
- Aucune stratégie identifiée ne rend l'espérance positive, à aucune cagnotte atteignable.

---

## Journal des corrections

Cette section conserve, dans l'ordre chronologique, chaque correction apportée à
l'analyse — y compris les erreurs que j'ai commises et qui ont été relevées. Elle sert
de trace de révision.

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

## Correction majeure — les données EuroDreams réelles (2023-2026)

297 tirages officiels, du 2023-11-06 au 2026-09-07, **tous un lundi (149) ou un
jeudi (148)**. 140,7 M€ misés, 56,3 M de grilles à 2,50 €.

### Le relevé du joueur EST bien EuroDreams

Avec un décalage de **un jour** (débit le lendemain du tirage) : 61/61 lignes se
rattachent à un tirage (60 à J-1, 1 à J-0) et **56/61 montants se reconcilient
exactement** avec les tables de gains réelles + Joker+. L'anomalie de calendrier
relevée précédemment a donc une explication bénigne, et la conclusion
« ce n'est pas EuroDreams » était **fausse**.

### La table de gains réelle remplace la table supposée

| Rang | Hypothèse de l'audit | Réalité mesurée (297 tirages) |
|---|---|---|
| R1 (6+D) | 7 200 000 € | 7 200 000 € **fixe** (2 gagnants) ✓ |
| R2 (6) | 120 000 € | 120 000 € **fixe** (13 gagnants) ✓ |
| R3 (5) | 500 € fixe | **parimutuel** : 34,70 → 990,50 €, médiane 125,20 € |
| R4 (4) | 20 ou 30 € fixe | **parimutuel** : 17,40 → 65,70 €, moyenne 38,75 € |
| R5 (3) | 5 € fixe | **parimutuel** : 3,00 → 7,90 €, moyenne 5,16 € |
| R6 (2) | 2,50 € fixe | 2,50 € **fixe** ✓ |

Les probabilités combinatoires du script 01 sont **confirmées** par les fréquences
réelles (ratio observé/théorique : 1,002 au rang 6, 1,006 au rang 5, 1,009 au rang 4).

### Le TRJ réel

```
TRJ mesuré sur 297 tirages          : 39,79 %   (dominé par 2 jackpots)
  hors rangs 1 et 2                 : 28,44 %   (théorique 28,46 % — exact)
TRJ de long terme, tables réelles   : 44,47 % nominal
                                      39,35 % actualisé à 3 %
TRJ officiel annoncé                : 52,00 %
```

L'écart de ~8 points avec les 52 % annoncés est donc **mesuré**, plus supposé.

**Changement de régime en octobre 2025** : la médiane du rang 3 passe de 103 € à
496 €, mais le TRJ des rangs 3-6 reste inchangé (28,54 % → 28,30 %). Simple
réallocation entre rangs : **effet nul pour le joueur.**

### Le benchmark du joueur, exact

Espérance calculée sur les tables réelles de ses 61 tirages effectifs :
gains EuroDreams attendus 173,28 € + Joker+ hors jackpot 42,82 € = **215,91 €**
attendus contre **231,90 €** encaissés, soit un ratio de **1,074**.
TRJ de portefeuille attendu 30,78 % contre 33,06 % observé.

## Application — `eurodreams_v3.html`

Outil autonome (un seul fichier, aucune dépendance) recalibré sur les données
officielles. Trois onglets : **Générateur**, **Bankroll**, **Données réelles**.

Corrections apportées par rapport à la v2 :

| v2 | v3 |
|---|---|
| Table de gains supposée (R3=500, R4=30, R5=5 fixes) | **table mesurée**, R3/R4/R5 parimutuels, sélecteur régime actuel / moyenne 297 tirages |
| Mise de 11,50 € traitée comme « 4,6 grilles EuroDreams » | **4 grilles à 2,50 € + 1 Joker+ à 1,50 €**, deux jeux simulés séparément |
| χ² à 39 ddl (seuil 54,6) | **loi nulle corrigée** pour un tirage sans remise : E[χ²] = 34, seuil réel ≈ 47,5, + avertissement de puissance |
| P(≥1 gain) par `1−(1−p)ⁿ` | **énumération exacte** des 3 838 380 tirages (l'approximation sous-estimait de 8,2 pts à 4 grilles) |
| « espérance ≈ −48 % » | **44,31 % nominal / 39,19 % actualisé**, mesuré |
| « l'écart aux 52 % vient de la réserve non redistribuée » | écart **mesuré** à −7,7 points, explication retirée |
| Levier anti-partage présenté comme « le seul levier réel » | **plafonné et chiffré** : quelques dixièmes de point (mesuré +0,44 pt sur Joker+) |
| — | onglet **Données réelles**, note sur le décalage J+1 des dates de débit, P(récupérer sa mise) exacte |

## v4 — l'onglet Cagnotte Joker+

`eurodreams_v4.html` ajoute un quatrième onglet consacré au seul levier de tout
l'audit qui dépasse le dixième de point.

**TRJ = 46,80 % + 5,92 points par million d'euros de cagnotte.**

Le rang 1 du Joker+ s'accumule (contrairement à EuroDreams, sans report) et les
rangs 2 à 8 sont à montants fixes : tout le TRJ variable tient dans cette cagnotte.

| Tranche | Part des tirages | TRJ moyen |
|---|---|---|
| 0,0–0,4 M€ | 17,3 % | 48,31 % |
| 0,4–0,8 M€ | 28,5 % | 49,98 % |
| 0,8–1,2 M€ | 21,6 % | 52,40 % |
| 1,2–1,6 M€ | 11,7 % | 54,83 % |
| 1,6–2,0 M€ | 7,0 % | 57,19 % |
| 2,0–2,5 M€ | 7,1 % | 59,97 % |
| 2,5–3,2 M€ | 6,7 % | 63,54 % |

Distribution mesurée sur les **1 178 tirages** où la cagnotte en cours est publiée
(2011-02-02 → 2016-01-24). Médiane 800 000 €, moyenne 1 031 515 €.

**Deux régimes.** 2011 → début 2016 : palier de +75 000 €/semaine, sommet
3 125 000 €. Depuis 2016 la cagnotte en cours n'est plus publiée ; les 38 jackpots
touchés sont tous multiples de 200 000 € et plafonnés à 2 500 000 €, ce qui ramène
le TRJ maximal atteignable de 65,3 % à **61,6 %**.

**La borne dure ne bouge pas** : espérance nulle à 8 989 301 €, soit 2,9× le record
historique et 3,6× le plafond actuel. Aucune fenêtre à espérance positive n'existe.

Le curseur de cagnotte de l'onglet Bankroll pilote le modèle : la loi de gain du
Joker+ est reconstruite à partir des paramètres mesurés (6 chiffres alignés par
l'une des deux extrémités + signe du zodiaque cumulatif) au lieu de constantes
figées, et l'espérance du portefeuille se recalcule.

Graphiques : palette de marques **validée** (`#3987e5` / `#d95926`, bande de clarté
OKLCH dark, ΔE CVD 26,8, contraste ≥ 3:1), survol avec réticule et infobulle,
légende, étiquettes directes sélectives, vue tableau.

## Analyse des fichiers `eurodreams-financialdata-FR-yyyy.csv`

`scripts/14_analyse_financiere_eurodreams.py` — 297 tirages, 4 fichiers,
0 doublon, 0 valeur manquante, écarts de 3 et 4 jours uniquement (lundi/jeudi).
140,69 M€ misés · 56,28 M de grilles · 26,85 M de participations · 2,08 grilles
par participation.

### Règle de répartition reconstituée

| Rang | Part de la mise | CV | Nature |
|---|---|---|---|
| R1 | 14,11 % | 12,21 | fixe (7 200 000 €, 2 versements) |
| R2 | 1,21 % | 4,73 | fixe (120 000 €, 13 versements) |
| R3 | 0,50 % | 0,90 | parimutuel |
| R4 | 3,36 % | 0,155 | parimutuel |
| R5 | 6,42 % | 0,099 | parimutuel |
| R6 | 18,17 % | 0,037 | fixe (2,50 €) |

Le changement d'octobre 2025, au millième près :

```
2023-11 → 2025-09 : R3 0,221 % | R4 3,554 % | R5 6,541 % | R6 18,135 % | total 28,451 %
2025-10 → 2026-09 : R3 1,082 % | R4 2,962 % | R5 6,171 % | R6 18,237 % | total 28,452 %
```

Le rang 3 est multiplié par 4,9, financé par les rangs 4 et 5. **Le total ne bouge
pas d'un millième.** Réallocation pure, effet nul pour le joueur.

### Les joueurs choisissent leurs numéros — et ça se mesure

Si les grilles étaient réparties au hasard, le nombre de gagnants suivrait une
binomiale exacte et les résidus standardisés auraient une variance de 1.

| Rang | p obs / p théo | Var(z) |
|---|---|---|
| R6 (2 n°) | 1,002 | **54,22** |
| R5 (3 n°) | 1,006 | **33,49** |
| R4 (4 n°) | 1,009 | 8,31 |
| R3 (5 n°) | 1,040 | 1,85 |
| *Joker+ (numéros non choisis)* | *1,000* | *2,20* |

La moyenne colle à la théorie à trois décimales ; la **variance est 54 fois trop
grande**. Le nombre de gagnants au rang 5 va de 3 678 à 18 891 (×5,1) là où le
bruit binomial donnerait ±2,8 %.

### Ce que vaut réellement le levier anti-partage sur EuroDreams

Le lot parimutuel est le pool divisé par les gagnants : ρ(sur-représentation des
gagnants, lot) = **−0,843** au rang 5, −0,665 au rang 4.

| | TRJ rangs 3-6 | écart |
|---|---|---|
| lot du décile bas (grille populaire) | 26,08 % | −2,38 pt |
| lot moyen | 28,46 % | — |
| lot du décile haut (grille impopulaire) | 31,36 % | **+2,89 pt** |

**Borne supérieure du levier : +2,89 points** — six fois plus que les +0,44 point
mesurés sur le Joker+, où les numéros ne sont pas choisis. C'est une borne : elle
suppose de toucher systématiquement le décile favorable, ce qu'aucune grille ne
garantit.

### Autres résultats

- Participation en chute : 386 457 grilles/tirage sur les 10 premiers tirages,
  149 668 sur les 10 derniers (**−61,3 %**, Spearman ρ = −0,290, p = 3,5·10⁻⁷).
- Aucune différence lundi / jeudi (p = 0,463). Creux estival marqué (juillet
  151 991 grilles contre 190 000 en moyenne).
- Rangs 1 et 2 parfaitement poissoniens : 2 jackpots observés pour 2,93 attendus
  (p = 0,88), 13 rangs 2 pour 11,73 (p = 0,79). Jamais de report, jamais de partage.
- TRJ hors rangs 1-2 **constant à 28,4 % sur les quatre années** (28,36 / 28,34 /
  28,56 / 28,46). TRJ total 39,79 %, gonflé par les 2 jackpots de 2025.
- 100 % des lots sont arrondis au dixième d'euro.

## Audit de la feuille officielle `statistiques-jokerplus-0826.xlsx`

`scripts/15_audit_feuille_statistiques.py` — 4 onglets : Palmarès des signes,
TOP 10 des mises, TOP 10 des gains, Résultats (5 050 tirages, 2011-02-02 →
2026-08-31).

### Contrôle croisé : concordance parfaite

| Contrôle | Résultat |
|---|---|
| Numéros identiques (feuille ↔ mes CSV) | **5 050 / 5 050** (100,0000 %) |
| Signes identiques | **5 050 / 5 050** |
| TOP 10 des mises | 10/10 au centime |
| TOP 10 des gains | 10/10 |
| Somme des apparitions = nombre de tirages | 5 050 = 5 050 |
| Zéros de tête conservés | 461 numéros (9,13 %) |

Les 7 tirages de septembre 2026 présents dans mes CSV sont absents : la feuille
s'arrête à août.

### Le « Palmarès » ne dit rien

```
χ² d'uniformité = 14,79 (11 ddl) → p = 0,1924
Écart max |z| = 1,93 (Verseau) ; max attendu par pur hasard = 1,94 en moyenne
P(max|z| ≥ 1,93) = 0,489
Écart le plus sorti − le moins sorti : 71 (Balance 454, Verseau 383)
   médiane attendue par pur hasard : 66  →  64ᵉ percentile
```

**Le palmarès officiel est exactement aussi dispersé qu'un palmarès tiré au sort.**

La colonne « plus sorti depuis (# tirages) » suit une loi géométrique(1/12)
(Kolmogorov-Smirnov p = 0,927) : l'attente est sans mémoire, un signe « en retard »
n'a aucune probabilité accrue de sortir.

### Tests d'indépendance que la feuille ne fait pas

| Test | Résultat |
|---|---|
| Table de transition 12×12 (signe t → t+1) | χ² = 103,4 (121 ddl), p = 0,874 |
| Même signe deux fois de suite | 9,01 % vs 8,33 % attendu, p = 0,083 |
| Chiffres, toutes positions (30 300 tirés) | χ² = 5,67 (9 ddl), p = 0,773 |
| Chiffres par position | p = 0,27 / 0,95 / 0,46 / 0,14 / 0,53 / 0,995 |
| Numéros complets répétés | 13 paires observées, 12,7 attendues |
| Autocorrélation du numéro (lag 1) | ρ = −0,004 |

### Puissance : ce que 5 050 tirages permettent

```
un signe 1,05× plus fréquent → détecté dans  7,1 % des cas
             1,10×           →               20,3 %
             1,15×           →               42,0 %
             1,20×           →               71,5 %
```

Quatre fois plus puissant que le test sur les 297 tirages EuroDreams (5,5 % contre
un biais de 1,10), mais un biais modéré resterait invisible.

### Les joueurs ne suivent pas le palmarès

Corrélation entre la fréquence publiée et la popularité mesurée auprès des joueurs
(via le rang 8) : **Spearman ρ = +0,249, p = 0,436**. Capricorne est le 2ᵉ signe le
plus sorti et le **moins joué** (indice 0,916) ; Lion est le plus joué (1,110) et
seulement 3ᵉ au palmarès. La préférence des joueurs a une autre origine.

## v5 — onglet « Popularité » (`eurodreams_v5.html`)

Cinquième onglet de l'application, qui rassemble les trois résultats mesurés sur la
manière dont les joueurs choisissent leurs grilles. Données produites par
`scripts/16_donnees_v5_popularite.py` → `out/v5_popularite.json`, embarquées en dur.

**1. Sur-dispersion du nombre de gagnants (297 tirages EuroDreams).** Si les grilles
étaient tirées au sort, le nombre de gagnants par rang suivrait une binomiale exacte
`B(n, p)` et les résidus standardisés `z = (k − np)/√(np(1−p))` auraient une variance
de 1. Mesuré : **1,85** (rang 3), **8,31** (rang 4), **33,49** (rang 5), **54,22**
(rang 6). Témoin : le Joker+, dont les numéros sont imprimés sur le ticket et non
choisis, donne **2,20**. L'écart entre les deux jeux est la signature du choix humain.

**2. Borne du levier anti-partage (déciles de fréquentation).** Les 297 tirages sont
classés par encombrement (résidu du rang 6) ; on calcule pour chaque décile
l'espérance de gain d'une grille, `Σ p_r × W_r`, où seuls les lots parimutuels bougent.
Résultat : **D1 = 31,63 %** de TRJ contre **28,46 %** en moyenne et **25,72 %** en D10,
soit une amplitude de **5,91 points** et une borne supérieure de **+3,17 points**.
Cette borne est inatteignable : l'encombrement dépend des numéros sortis, pas de la
grille. Le levier réellement mesurable (Joker+, 642 M de grilles) vaut **+0,44 point**,
au mieux **+0,57 point** en combinant signe et chiffres.

*Correction :* la valeur de +2,89 points annoncée au tour précédent était erronée ;
le calcul par déciles refait ici donne **+3,17 points**.

**3. Les joueurs ne suivent pas les statistiques officielles.** Nuage de points
« sorties publiées par la Loterie » × « part réellement jouée » (mesurée par le rang 8
du Joker+, bon signe seul), sur les 5 050 tirages de la feuille officielle.
**Spearman ρ = +0,249 (p = 0,436)** : aucune relation. Capricorne est le 2ᵉ signe le
plus sorti et le moins joué (0,916) ; Lion est le plus joué (1,110) et seulement 3ᵉ au
palmarès. La popularité est culturelle, donc stable (ρ = +0,944 entre 2011-2018 et
2019-2026) — donc exploitable durablement, contrairement à un biais de tirage qui
n'existe pas.

Graphiques : barres horizontales en échelle logarithmique (sur-dispersion), barres
divergentes autour de la moyenne (déciles), nuage de points avec étiquetage
non chevauchant (signes). Palette de marques `#3987e5` / `#d95926` validée sur la
surface `#0d1117` (bande de clarté OKLCH, ΔE CVD 26,8, contraste ≥ 3:1).

## Contre-audit : trois objections externes, testées (`scripts/17_contre_audit_reglement.py`)

Trois objections m'ont été opposées sur la base du règlement officiel. Les trois sont
fondées ; la v5 de l'application est corrigée en conséquence. Aucune ne change le TRJ
du joueur, deux changent l'interprétation et une change un chiffre.

**O1 — Le Fonds de Réserve explique les 7,5 points manquants. VALIDÉE.**
Le règlement EuroDreams prévoit que 45,21 % de l'« argent des lots » (= 52 % des mises)
part au Fonds de Réserve, qui finance les rangs 1-2 et les tirages/promotions. Le
reliquat, `52 % × (1 − 45,21 %) = 28,4908 %`, doit aller aux rangs 3-6. Je mesure
**28,4430 %** sur 297 tirages : concordance à **0,048 point**. Le Fonds reçoit
`52 % × 45,21 % = 23,5092 %` de la mise alors que l'espérance des rangs 1-2 n'en
consomme que **16,0068 %** — différence **7,5024 %**, soit exactement l'écart que je
constatais. Il n'était donc pas inexpliqué mais structurel : les 52 % sont exacts au
niveau de la famille de jeux, faux au niveau d'un tirage ordinaire. TRJ du joueur
inchangé : 44,45 % nominal, 39,35 % actualisé.

**O2 — Les probabilités Joker+ des rangs 1 et 2 doivent être structurelles. VALIDÉE.**
La loi « k chiffres alignés depuis l'une des deux extrémités », `p = 2 × 0,9 × 10⁻ᵏ`,
est vérifiée à quatre décimales sur 642 M de grilles (ratios observé/théorique :
0,9999 · 0,9996 · 1,0006 · 0,9992 · 1,0032 pour les rangs 7 à 3). Pour k = 6 les deux
extrémités se confondent, donc `p = 10⁻⁶` exactement, réparti 1/12 – 11/12 par le
signe. Mes constantes empiriques (1/11 265 001 et 1/1 052 631) reposaient sur 57 et 610
événements ; les valeurs structurelles (**1/12 000 000** et **11/12 × 10⁻⁶**) tombent
dans leurs IC95 (57 observés contre 53,5 attendus, p = 0,67). Conséquences : la pente
de cagnotte passe de 5,92 à **5,56 points de TRJ par million**, le seuil d'espérance
nulle de 8 989 302 € à **9 575 820 €**, et le modèle colle mieux au réel — il prédit
52,53 % contre 52,39 % effectivement versés, là où l'ancienne pente donnait 52,90 %.

**O3 — Les 6 chiffres du Joker+ ne sont pas choisis par le joueur. VALIDÉE.**
Seul le signe du zodiaque est choisi. Mes propres mesures le confirment : l'amplitude
de la part jouée vaut **×1,213** pour les signes contre **×1,011** (1er chiffre) et
**×1,007** (dernier chiffre) — un excès 19 fois plus grand d'un côté que de l'autre.
L'écart de ~1 % sur les chiffres est réel et significatif sur 642 M de grilles, mais il
provient du stock de numéros attribués aux tickets, pas d'un choix humain, et n'est de
toute façon pas exploitable. Le levier anti-partage Joker+ tombe donc de **+0,572
point** (signe + chiffres) à **+0,436 point** (signe seul). Ce que l'objection ne
touche pas : la sur-dispersion EuroDreams (Var(z) = 54,22 au rang 6), où les numéros
sont bien cochés par le joueur — elle la renforce, en faisant du Joker+ à Var(z) = 2,20
un témoin propre de ce que donne un jeu à grilles non choisies.

## v6 — audit correctif (`eurodreams_v6.html`, `scripts/18_v6_modele_exact.py`)

La v5 reste en place comme référence. La v6 reprend cinq points un par un ; deux de mes
chiffres tombent, un troisième est requalifié.

### 1. Les 52 % et le Fonds de Réserve
Porté dans `README`, `eurodreams_v6.html`, `scripts/14` et `scripts/00`. Le règlement
affecte 45,21 % de l'argent des lots (= 52 % des mises) au Fonds de Réserve, qui finance
les rangs 1-2 et les promotions ; il reste `52 % × (1 − 45,21 %) = 28,4908 %` pour les
rangs 3-6, contre **28,4623 %** mesurés — 0,028 point d'écart. Le solde de **7,50 points**
part en tirages exceptionnels et provision. Sur **EuroDreams Boost** : aucune trace dans
les fichiers financiers (rang 1 toujours 7 200 000 €, rang 2 toujours 120 000 €, part 3-6
jamais à plus de 1,5 point de sa médiane), ce qui est cohérent avec un financement hors
table de gains, mais je ne peux pas le vérifier — l'accès à `loterie-nationale.be` est
bloqué depuis cet environnement.

### 2. PMF Joker+ refaite depuis les règles
Plus aucun paramètre ajusté. Lots fixes vérifiés sur 5 057 tirages ; loi
`p(k) = 2 × 0,9 × 10⁻ᵏ` confrontée rang par rang. **Découverte au passage :** la lecture
combinatoire stricte — un seul lot par ticket, `P(max(L,T) = 1) = 0,1701` — est **rejetée
à 667 σ** au rang 7, où l'on observe 0,17999. Un ticket qui aligne un chiffre à *chaque*
extrémité est payé **deux fois**. À k = 6 les deux lectures se confondent, d'où
`P(R1) = 1/12 000 000` et `P(R2) = 11/12 × 10⁻⁶` (57 jackpots observés contre 53,5
attendus, p = 0,67 ; 610 rangs 2 contre 588,6, p = 0,39). Le lot « signe » de 1,50 € est
cumulatif : `P(R8)` observée = 0,083311 contre 1/12 = 0,083333, et non 0,0667.
**Contrôle du modèle : 46,7555 % prédits hors jackpot contre 46,8010 % réellement versés
sur 963 M€ — 0,045 point d'écart.** Pente de cagnotte `10⁻⁶/12 ÷ 1,50 €` =
**5,5556 points par million**, seuil d'espérance nulle **9 584 002 €**, tranches et
`PMISE_AVEC` recalculés sur cette PMF (les `PMISE` ne bougent pas : le jackpot est trop
rare pour peser sur un seuil « gain ≥ mise »).

### 3. Popularité des chiffres supprimée, vrai modèle de co-gagnants pour le signe
Le +0,436 / +0,572 point est retiré. Modèle exact, puisque tout y est connu — le signe est
choisi, les chiffres non, et le rang 1 est le seul lot partagé :
`K ~ Poisson(λ)`, `λ = n × 10⁻⁶ × q(signe)`, gain `J/(1+K)`, avec n = 139 883 grilles par
tirage (médiane) et q mesurée sur le rang 8. Résultat : λ ≈ **0,011**, donc
`E[1/(1+K)]` varie de 0,994679 (Capricorne) à 0,993553 (Lion).
**Valeur réelle du levier : +0,0050 point** de TRJ (Capricorne contre Lion) à la cagnotte
médiane, +0,0197 point au record historique. L'ancien chiffre divisait la cagnotte par le
nombre *attendu* de gagnants comme s'il y en avait toujours plusieurs. Contrôle : **un
seul jackpot partagé sur 57** en seize ans, là où ce modèle en attend 0,66.

### 4. Le +3,17 point EuroDreams requalifié
Ce n'est pas une borne de levier mais une **amplitude empirique constatée a posteriori** :
elle décrit combien le TRJ d'un *tirage* varie selon l'affluence sur *les numéros sortis*,
et le décile ne se choisit pas. Ce que les données permettent en revanche, c'est
d'estimer le modèle hiérarchique `W_r | tirage ~ Binomiale(n, p_r × M_r)`, d'où
`Var(z) ≈ 1 + n·p·Var(M)` :

| rang | gagnants attendus | Var(z) | écart-type de M |
|---|---|---|---|
| Rang 6 — 2 n° | 34 340 | 54,22 | **3,9 %** |
| Rang 5 — 3 n° | 5 908 | 33,49 | **7,4 %** |
| Rang 4 — 4 n° | 415 | 8,31 | **13,3 %** |
| Rang 3 — 5 n° | 10 | 1,85 | **29,1 %** |

**Ce qui manque** pour un modèle prédictif grille → co-gagnants : les 297 combinaisons
tirées (6 numéros + Dream), absentes des fichiers financiers. Il faudrait les
`eurodreams-gamedata-FR-2023…2026.csv`, pendant EuroDreams des `jokerplusgamedata` déjà
fournis.

### Bug corrigé au passage
Les CSV EuroDreams utilisent le **point** décimal (`579917.50`), les CSV Joker+ la
**virgule** avec point de milliers (`2.000,00`). Le lecteur commun de `scripts/18`
supprimait le point pour tout le monde et multipliait les mises EuroDreams par 100.
Corrigé en tranchant sur la présence d'une virgule. Les résultats des scripts antérieurs
ne sont pas touchés : ils utilisaient `astype(float)` pour EuroDreams, et les ratios
pool/mise sont de toute façon invariants d'échelle.

## v6 — deuxième passe : le Boost, la PMF exacte et les bugs applicatifs

### Le mystère des 52 % est clos, et l'explication est exacte au dix-millième

`scripts/19_v6_boost_et_pmf_exacte.py`. Ma formulation précédente — le solde du Fonds de
Réserve part « en promotions, tirages exceptionnels et provision » — était vague. Le
mécanisme est arithmétiquement identifiable :

| | part de la mise |
|---|---|
| Le Fonds de Réserve reçoit `52 % × 45,21 %` | **23,5092 %** |
| Les rangs 1-2 en consomment (rente 7,2 M€) | 16,0068 % |
| **Solde disponible** | **+7,5024 %** |
| Coût d'un **Boost** (rente portée à 10,8 M€) | **+7,5032 %** |
| **Écart** | **0,0008 point** |

Le Fonds met de côté, sur chaque tirage ordinaire, exactement ce qu'il faut pour financer
un tirage Boost. Et en régime Boost :
`28,4908 % + 1,0004 % + 22,5095 % = ` **52,0007 %**. Les 52 % annoncés ne sont ni un
arrondi ni une moyenne : c'est le TRJ nominal exact d'un tirage boosté.

**Pourquoi le Boost est invisible dans les fichiers** — 55 tirages belges tombent dans la
fenêtre du 02/10/2025 au 09/04/2026 ; aucun n'en porte la trace, parce que la colonne du
lot de rang 1 vaut 0,00 € tant qu'il n'y a pas de gagnant belge, et que les deux seuls
jackpots belges de l'historique (01/05/2025 et 07/07/2025) sont antérieurs au Boost —
remporté au Portugal. Mon constat « aucune trace » était exact, mon explication ne l'était
pas.

### PMF Joker+ : le double comptage est corrigé

La v5 et la première v6 posaient `P(gain de 2 €) = 0,18`. C'est un **double comptage** : un
ticket peut aligner un chiffre à gauche *et* un à droite. La loi exacte s'obtient en
énumérant le couple `(L, T)` = chiffres alignés à gauche / à droite :

```
P(L=l, T=t) = 0,81 × 10^-(l+t)   si l+t ≤ 4   (deux positions bloquantes distinctes)
            = 0,9 × 10⁻⁵         si l+t = 5   (elles se confondent)
            = 10⁻⁶               si l = t = 6 (numéro entier)
```

Somme exacte = 1. Contrôles : `E[nb de lots de rang 7] = 2 × 0,09 = 0,18` (observé
0,179985 sur 642 M de grilles) **et** `P(le ticket gagne) = 0,19 + 0,81/12 = 25,75 % =
1 sur 3,883` — le « 1 sur 3,88 » officiel. Les deux lectures sont vraies parce que `P-R7`
compte des **lots**, pas des tickets. L'espérance ne bouge pas (linéarité) : 46,7555 %
hors jackpot. Mais la **loi** change — 25 valeurs de gain distinctes au lieu de 12 — et
donc `PMISE_AVEC` :

| grilles | v5/v6a | v6 exacte |
|---|---|---|
| 1 | 9,7460 % | **10,2083 %** |
| 2 | 3,4799 % | **3,7455 %** |
| 3 | 1,5052 % | **1,6125 %** |
| 4 | 1,1807 % | **1,2237 %** |

### Le test des 61 tirages : simulation du modèle, pas bootstrap
Le bootstrap rééchantillonne les gains observés : il mesure l'incertitude autour de la
moyenne empirique, pas la conformité au modèle. En simulant 61 tirages **sous le modèle**
(200 000 réplications) : médiane **28,64 %**, IC 90 % **[22,97 % ; 38,56 %]**, moyenne
32,00 % (tirée par un jackpot que 61 tirages ne verront pas). Le TRJ observé de 33,06 %
est au **81ᵉ percentile** — au-dessus de la médiane, donc de la chance. L'ancien « IC de
24,6 points » répondait à une autre question.

### Puissance du χ² recalibrée
`scripts/04`. Le poids passé à l'échantillonnage sans remise ne produit pas un ratio de
fréquence égal à ce poids : le script tabulait la puissance contre une alternative qui
n'était pas celle annoncée. Les poids sont désormais **calibrés** par dichotomie sur
200 000 tirages simulés. Puissance sur 297 tirages : 4,8 % (×1,05), **6,0 %** (×1,10),
9,5 % (×1,20), 38,2 % (×1,50).

### Bankroll : le Boost est pris en compte
L'espérance est calculée ligne à ligne ; pour un tirage de la fenêtre Boost le rang 1 vaut
10,8 M€. Sur l'historique de démonstration : **33 tirages en régime Boost, +24,76 €**
d'espérance nominale que les versions précédentes ignoraient. Cela ne change évidemment
ni les gains réels ni l'analyse hors jackpot.

### Bugs applicatifs corrigés
- **`PMISE_SANS` affichée hors de son domaine** : elle est tabulée pour des grilles
  disjointes ; elle n'apparaît plus en mode « Indépendantes ».
- **Plus de 6 grilles disjointes** : impossible (6 × 6 = 36 numéros sur 40). Le générateur
  plafonne explicitement et affiche un avertissement, au lieu de retourner silencieusement
  moins de grilles que demandé.
- **`toISOString()`** renvoyait la date UTC : en Belgique, entre minuit et 2 h, la saisie
  était datée de la veille. Remplacé par un formatage en heure locale.
- **Divisions par zéro** (historique d'une seule ligne, mise nulle) : helper `div()` qui
  renvoie `null`, affiché « — ».
- **Contradiction du générateur** : « l'espérance est identique quelle que soit la grille »
  est faux avec des rangs parimutuels. Reformulé : la *probabilité de sortir* est identique,
  l'espérance varie de quelques dixièmes de point selon la popularité.
- Le `<title>` disait encore « v3 ».

### Scripts marqués LEGACY
`00_audit_complet_colab.py` (table de gains supposée), `09` et `10` (lecture des chiffres
Joker+ comme signature humaine, et valorisation du levier). Bandeau en tête de fichier.

