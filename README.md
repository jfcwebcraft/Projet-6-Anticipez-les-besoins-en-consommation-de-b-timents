# Projet 6 : Anticipez les besoins en consommation de bâtiments de Seattle

Ce dépôt contient l'ensemble des travaux réalisés pour prédire la consommation d'énergie des bâtiments non résidentiels de la ville de Seattle à partir de leurs caractéristiques structurelles (taille, usage, année de construction).

Le projet est divisé en deux parties : la modélisation prédictive (Partie 1) et l'exposition du modèle via une API de production (Partie 2).

## Structure du projet

* **01_Analyse_Exploratoire.ipynb** : Analyse exploratoire des données (EDA), étude de la variable cible, nettoyages initiaux (exclusion du résidentiel) et insights clés.
* **02_Modelisation_Supervisee.ipynb** : Feature engineering, gestion des valeurs aberrantes (outliers par catégorie avec la méthode IQR), comparaison d'algorithmes (Régression Linéaire, RandomForest, GradientBoosting), optimisation par GridSearchCV et exportation du modèle final.
* **service.py** : Logique de l'API de serving BentoML chargeant le modèle entraîné pour réaliser des prédictions.
* **validation.py** : Schéma de validation Pydantic contrôlant la cohérence des données soumises à l'API (validation physique et métier).
* **test_api.py** : Script de test unitaire pour valider le fonctionnement et la robustesse des endpoints locaux de l'API.
* **bentofile.yaml** : Fichier de configuration BentoML pour empaqueter le service et générer le conteneur de production.
* **2016_Building_Energy_Benchmarking.csv** : Jeu de données brut d'enquête de la ville de Seattle pour l'année 2016.
* **model/** : Dossier contenant le modèle sauvegardé (`best_model.joblib`) et la liste ordonnée des variables explicatives (`feature_names.json`).

## Installation et Utilisation

### 1. Initialiser l'environnement virtuel

Pour exécuter les notebooks ou lancer l'API en local, créez et activez un environnement virtuel Python, puis installez les dépendances nécessaires :

```powershell
# Création de l'environnement virtuel
python -m venv .venv

# Activation (PowerShell sous Windows)
.venv\Scripts\Activate.ps1

# Installation des dépendances
pip install -r requirements-notebook.txt
```

### 2. Exécuter l'API de Prédiction (BentoML)

Pour démarrer le service de serving en local sur le port `3000` (port par défaut) :

```powershell
# Démarrage du service
.venv\Scripts\python -m bentoml serve service:EnergyPredictionService --port 3000
```

Vous pouvez ensuite tester le fonctionnement de l'API en lançant le script de test dans un autre terminal :

```powershell
python test_api.py
```

### 3. Empaqueter avec BentoML (Génération du conteneur)

Pour construire le bento et préparer le déploiement Docker :

```powershell
# Build du Bento
.venv\Scripts\bentoml build -f bentofile.yaml
```
