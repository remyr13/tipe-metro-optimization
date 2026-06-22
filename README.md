2# tipe-metro-optimization
TIPE — Optimisation de réseaux de métro : définition d'une fonction d'inefficacité globale, conception d'un algorithme glouton comme solution de base, puis amélioration par recuit simulé. Analyse des performances comparées. Python.
# Optimisation d'un réseau de métro

TIPE - MP*, lycée La Martinière Montplaisir, Lyon.

## Problème étudié

Comment concevoir un réseau de métro efficace pour une ville donnée ?

Pour répondre à cette question, j'ai défini une fonction d'inefficacité qui permet de mesurer si un réseau est bon ou mauvais. Elle prend en compte deux choses : la distance moyenne qu'un usager doit parcourir pour aller d'une station à une autre (en tenant compte des correspondances et des arrêts), et la longueur totale des tunnels à creuser et entretenir. L'objectif est de minimiser cette fonction.

Les stations sont supposées réparties sur un disque, avec un poids inversement proportionnel à leur distance au centre (modèle de Clark), ce qui reflète le gradient de densité d'une ville réelle.

## Hypothèses de travail

Le modèle ignore plusieurs contraintes réelles : contraintes géographiques et géologiques, capacité des rames, vitesse variable. Les simplifications principales sont :
- vitesse constante et distance de voyage = distance euclidienne
- chaque station n'apparaît qu'une seule fois par ligne (sauf terminus d'une ligne circulaire)
- nombre de lignes fixé au début de la simulation

## Déroulement du projet

### 1. Algorithme glouton (`evolution_reseau.py`)

Le premier algorithme explore à chaque étape toutes les modifications locales possibles du réseau et retient celle qui réduit le plus l'inefficacité. Trois opérations sont possibles : ajouter une station sur une ligne, en supprimer une, ou échanger deux stations. Le problème principal est qu'il ne donne accès qu'à un optimum local.

### 2. Heuristique de départ (`creation_du_reseau.py`)

Plutôt que de partir d'un réseau aléatoire, j'ai conçu un algorithme qui génère un réseau initial en forme d'étoile, dont la structure se retrouve dans beaucoup de réseaux de métro réels. Cela améliore significativement le point de départ de l'optimisation.

### 3. Recuit simulé (`recuit_simule.py`)

Pour dépasser les limitations du glouton, j'ai implémenté un algorithme de recuit simulé. La différence clé : il peut accepter des modifications qui dégradent temporairement le réseau, avec une probabilité `exp(-dI / T)`, où T est une température qui diminue au fil de l'algorithme (`T <- gamma * T` à chaque génération). Cela permet d'éviter de rester bloqué dans un optimum local.

### 4. Analyse des résultats (`analyse_data.py`)

Comparaison des deux algorithmes et étude de l'influence du nombre de lignes (droites et circulaires) sur l'inefficacité finale. Application au réseau de métro de Lyon pour comparer le réseau réel au réseau optimisé.

## Fichiers

- `reseau2.py` : structure de données principale (classe `Reseau2`)
- `creation_du_reseau.py` : génération de réseaux initiaux
- `evolution_reseau.py` : algorithme glouton
- `recuit_simule.py` : algorithme de recuit simulé
- `analyse_data.py` : analyse et visualisation des résultats
- `lyon.py` : application au réseau de métro de Lyon
- `paris.py` : application au réseau de métro de Paris

## Dépendances

numpy, matplotlib

Installation : `pip install numpy matplotlib`
