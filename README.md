# Tableau de Bord de Gestion des Dons de Sang

Ce projet est un tableau de bord complet pour la gestion et l'analyse des dons de sang au Cameroun, comprenant une interface utilisateur web interactive et une API de prédiction d'éligibilité basée sur l'apprentissage automatique.

## 🌟 Fonctionnalités Principales

### 📊 Dashboard Web
1. **Profils des Donneurs**
   - Analyse démographique détaillée (âge, genre, profession)
   - Segmentation des donneurs par région et niveau d'éducation
   - Visualisation des tendances de don par période

2. **Analyse des Campagnes**
   - Suivi des performances des campagnes de don
   - Cartographie des zones d'intervention
   - Statistiques de participation par région

3. **Analyse de Santé**
   - Suivi des indicateurs de santé des donneurs
   - Analyse des critères d'éligibilité
   - Identification des facteurs de risque

4. **🔮 Prédiction d'Éligibilité**
   - Modèle ML pour prédire l'éligibilité des donneurs
   - Interface intuitive pour la saisie des données
   - Résultats instantanés avec score de confiance

5. **📈 Rétention des Donneurs**
   - Analyse des taux de retour des donneurs
   - Identification des facteurs de fidélisation
   - Suggestions pour améliorer la rétention

6. **💭 Analyse des Retours**
   - Suivi de la satisfaction des donneurs
   - Analyse des commentaires et suggestions
   - Recommandations d'amélioration

### 🔧 API REST
- Endpoint de prédiction d'éligibilité
- Documentation interactive avec Swagger UI
- Sécurité et validation des données

## 🚀 Installation

1. **Prérequis**
   - Python 3.8 ou supérieur
   - pip (gestionnaire de paquets Python)
   - Git

2. **Cloner le dépôt**
```bash
git clone <url-du-repo>
cd Indaba-competition
```

3. **Créer un environnement virtuel**
```bash
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
# ou
myenv\Scripts\activate  # Windows
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

## 🎯 Démarrage

### 1. Démarrer l'API de Prédiction
#### a) Entrainer d'abord le model pour le premier lancement

```bash
cd api
python3 models/train_model.py
```
#### b) Demarrer l'api.
```bash
cd api
uvicorn main:app --reload --port 8000
```
L'API sera accessible à :
- Interface : http://localhost:8000
- Documentation : http://localhost:8000/docs

### 2. Lancer le Dashboard Web
Dans un nouveau terminal :
```bash
python app.py
```
Le dashboard sera accessible à : http://localhost:8050



## 🛠️ Technologies Utilisées

- **Frontend**
  - Dash (Framework Python pour applications web)
  - Plotly (Visualisations interactives)
  - Dash Bootstrap Components (UI Components)

- **Backend**
  - FastAPI (API REST)
  - scikit-learn (Machine Learning)
  - pandas (Manipulation de données)
  - NumPy (Calculs numériques)

- **Base de données**
  - SQLite (Stockage local)
  - pandas (Gestion des données)

## 📊 Modèle de Prédiction

Le modèle de prédiction d'éligibilité utilise un Random Forest Classifier entraîné sur des données historiques de dons de sang. Il prend en compte :
- Données démographiques (âge, genre)
- Niveau d'éducation
- Historique médical
- Antécédents de don
- Facteurs de risque

Précision du modèle :
- Score d'entraînement : 99.2%
- Score de test : 95.1%

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :
1. Forkez le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Équipe

- HOPE- Développeur Principal
- Équipe Indaba - Supervision et Support

## 📞 Contact

Pour toute question ou suggestion :
- Email : juniortakos4@gmail.com
- GitHub : [Junior-Mbogneng]
