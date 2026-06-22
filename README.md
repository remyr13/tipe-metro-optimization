2# tipe-metro-optimization
TIPE — Optimisation de réseaux de métro : définition d'une fonction d'inefficacité globale, conception d'un algorithme glouton comme solution de base, puis amélioration par recuit simulé. Analyse des performances comparées. Python.
# Optimisation d'un réseau de métro

TIPE (Travail d'Initiative Personnelle Encadré) — MP*, lycée La Martinière Montplaisir, Lyon.

## Problème étudié

Comment concevoir un réseau de métro efficace pour une ville donnée ?

L'objectif est d'optimiser la topologie d'un réseau de transport en commun (quelles stations desservir sur quelles lignes, dans quel ordre) en minimisant une **fonction d'inefficacité globale** du réseau. Cette fonction pénalise les trajets longs entre stations, en tenant compte des correspondances et du poids démographique de chaque station.

## Structure du projet

```
├── reseau2.py            # Structure de données principale : classe Reseau2
├── creation_du_reseau.py # Génération de réseaux initiaux (aléatoires ou en étoile)
├── evolution_reseau.py   # Algorithme glouton
├── recuit_simule.py      # Algorithme de recuit simulé
├── analyse_data.py       # Analyse et visualisation des résultats
├── lyon.py               # Application au réseau de métro de Lyon
└── paris.py              # Application au réseau de métro de Paris
```

## Démarche algorithmique

### 1. Définition de la fonction d'inefficacité

La fonction d'inefficacité agrège, pour toutes les paires de stations, la distance de trajet réelle (en tenant compte des correspondances et des arrêts) pondérée par l'importance de chaque station. Un réseau parfait aurait une inefficacité de 1.

### 2. Algorithme glouton (`evolution_reseau.py`)

Un premier algorithme glouton explore à chaque étape toutes les modifications locales possibles du réseau (ajout, suppression ou échange de stations sur une ligne) et retient celle qui réduit le plus l'inefficacité. Simple et rapide, il converge rapidement vers un optimum local.

### 3. Recuit simulé (`recuit_simule.py`)

Pour pallier les limitations de l'approche gloutonne (blocage dans des optima locaux), un algorithme de recuit simulé est implémenté. Il accepte avec une certaine probabilité des modifications qui dégradent temporairement le réseau, ce qui lui permet d'explorer plus largement l'espace des solutions. La probabilité d'acceptation décroît au fil des itérations selon une température qui diminue par un coefficient `pertes` à chaque génération.

Les trois types de modifications possibles à chaque étape sont :
- **Suppression** d'une station sur une ligne
- **Ajout** d'une station à une position donnée sur une ligne
- **Échange** de deux stations sur une ligne

### 4. Analyse des résultats (`analyse_data.py`)

Comparaison des performances des deux algorithmes sur des réseaux générés aléatoirement, avec visualisation de l'évolution de l'inefficacité au fil des générations.

## Dépendances

```
numpy
matplotlib
```

Installation :
```bash
pip install numpy matplotlib
```

## Exemple d'utilisation

```python
from creation_du_reseau import *
from recuit_simule import *

# Générer un réseau aléatoire de 20 stations, 3 lignes droites, 1 ligne circulaire
coordonnees = cree_coord_poids_centre(20, nb_stations=20)
reseau = cree_proto_reseau_etoile(coordonnees, nb_droite=3, nb_circ=1)

# Optimiser par recuit simulé
meilleur, inefficacites, _ = evolution_vrai_rs(reseau, debut_temperature=1e-5, pertes=0.99)
```

## Application à des réseaux réels

Les fichiers `lyon.py` et `paris.py` appliquent la fonction d'inefficacité aux réseaux de métro réels de Lyon et Paris, permettant de comparer l'efficacité théorique de ces réseaux selon le modèle défini.
