import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from datetime import datetime
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EligibilityModel:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.features = None
        
    def preprocess_data(self, df):
        """Prétraitement des données"""
        logger.info("Début du prétraitement des données")
        
        # Copie des données pour éviter la modification de l'original
        df_processed = df.copy()
        
        # Vérifier que toutes les features nécessaires sont présentes
        for feature in self.features:
            if feature not in df_processed.columns:
                df_processed[feature] = 'inconnu'
        
        # Encoder les variables catégorielles
        for col in df_processed.select_dtypes(include=['object']):
            if col in self.encoders:
                # Gérer les nouvelles catégories
                df_processed[col] = df_processed[col].astype(str)
                known_categories = set(self.encoders[col].classes_)
                logger.info(f"Catégories connues pour {col}: {sorted(known_categories)}")
                logger.info(f"Valeur reçue pour {col}: {df_processed[col].values[0]}")
                
                # Si la valeur n'est pas dans les catégories connues, utiliser la première catégorie comme valeur par défaut
                if df_processed[col].values[0] not in known_categories:
                    logger.warning(f"Valeur inconnue '{df_processed[col].values[0]}' pour {col}, utilisation de la valeur par défaut '{self.encoders[col].classes_[0]}'")
                    df_processed[col] = self.encoders[col].classes_[0]
                
                df_processed[col] = self.encoders[col].transform(df_processed[col])
        
        return df_processed
    
    def train(self, data_path):
        """Entraînement du modèle"""
        logger.info(f"Chargement des données depuis {data_path}")
        # Chargement des données
        df = pd.read_csv(data_path)
        
        # Prétraitement
        logger.info("Préparation des features")
        X = df[['age', 'genre', 'niveau_d_etude', 'situation_matrimoniale_(sm)',
                'profession', 'religion', 'a_t_il_elle_deja_donne_le_sang']]
        y = (df.iloc[:, 12] == 'eligible').astype(int)
        
        # Encodage des variables catégorielles
        self.features = X.columns.tolist()
        self.encoders = {}
        for feature in self.features:
            if X[feature].dtype == 'object':
                logger.info(f"Création d'un nouvel encodeur pour {feature}")
                self.encoders[feature] = LabelEncoder()
                X[feature] = self.encoders[feature].fit_transform(X[feature].fillna('inconnu'))
        
        # Standardisation des variables numériques
        numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_features) > 0:
            logger.info(f"Standardisation des features numériques : {numeric_features.tolist()}")
            scaler = StandardScaler()
            X[numeric_features] = scaler.fit_transform(X[numeric_features])
        
        # Division train/test
        logger.info("Division train/test")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entraînement du modèle
        logger.info("Entraînement du modèle")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Évaluation du modèle
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        logger.info(f"Score d'entraînement : {train_score:.3f}")
        logger.info(f"Score de test : {test_score:.3f}")
        
        return train_score, test_score
    
    def predict(self, features_dict):
        """Prédiction pour un nouveau donneur"""
        logger.info("Début de la prédiction")
        if self.model is None:
            raise ValueError("Le modèle n'a pas été entraîné")
        
        # Conversion en DataFrame
        logger.info(f"Features reçues : {features_dict}")
        df = pd.DataFrame([features_dict])
        
        # Renommer les colonnes si nécessaire
        if 'situation_matrimoniale' in df.columns:
            df = df.rename(columns={'situation_matrimoniale': 'situation_matrimoniale_(sm)'})
        if 'a_deja_donne' in df.columns:
            df = df.rename(columns={'a_deja_donne': 'a_t_il_elle_deja_donne_le_sang'})
            df['a_t_il_elle_deja_donne_le_sang'] = df['a_t_il_elle_deja_donne_le_sang'].map({True: 'oui', False: 'non'})
        
        # Prétraitement
        logger.info("Prétraitement des features")
        df_processed = self.preprocess_data(df)
        logger.info(f"Features prétraitées : {df_processed.to_dict()}")
        
        # Prédiction
        logger.info("Calcul de la prédiction")
        prediction = self.model.predict_proba(df_processed)[0]
        
        result = {
            'eligibilite': bool(prediction[1] > 0.5),
            'probabilite': float(prediction[1])
        }
        logger.info(f"Résultat de la prédiction : {result}")
        
        return result
        
    def save(self, model_path):
        """Sauvegarde du modèle"""
        if self.model is None:
            raise ValueError("Le modèle n'a pas été entraîné")
        
        # Création du dossier si nécessaire
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Sauvegarde du modèle et des préprocesseurs
        model_data = {
            'model': self.model,
            'encoders': self.encoders,
            'features': self.features
        }
        logger.info(f"Sauvegarde du modèle dans {model_path}")
        joblib.dump(model_data, model_path)
    
    def load(self, model_path):
        """Chargement du modèle"""
        logger.info(f"Chargement du modèle depuis {model_path}")
        model_data = joblib.load(model_path)
        self.model = model_data['model']
        self.encoders = model_data['encoders']
        self.features = model_data['features']
        logger.info("Modèle chargé avec succès")

if __name__ == '__main__':
    # Exemple d'utilisation
    model = EligibilityModel()
    
    # Chemin absolu vers les données
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(current_dir), 'data', 'processed_data.csv')
    model_path = os.path.join(current_dir, 'eligibility_model.joblib')
    
    # Entraînement
    train_score, test_score = model.train(data_path)
    
    # Sauvegarde du modèle
    model.save(model_path)
    
    # Test de prédiction
    example_donor = {
        'age': 30,
        'genre': 'Homme',
        'niveau_d_etude': 'Universitaire',
        'situation_matrimoniale': 'Célibataire',
        'profession': 'Ingénieur',
        'religion': 'chretien (catholique)',
        'a_deja_donne': True
    }
    
    prediction = model.predict(example_donor)
    print(f"\nPrédiction pour le donneur exemple :")
    print(f"Éligible : {prediction['eligibilite']}")
    print(f"Probabilité : {prediction['probabilite']:.2f}")
