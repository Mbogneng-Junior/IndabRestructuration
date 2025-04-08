import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def train_eligibility_model():
    """Entraîne le modèle de prédiction d'éligibilité et sauvegarde le modèle et l'encodeur"""
    
    # Charger les données
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed_data.csv')
    df = pd.read_csv(data_path)
    
    # Sélectionner les features pertinentes
    features = [
        'age', 'genre', 'niveau_d_etude', 'situation_matrimoniale_(sm)',
        'profession',
        'religion', 'a_t_il_elle_deja_donne_le_sang'
    ]
    
    # Préparer les données
    X = df[features].copy()
    y = (df['eligibilite_au_don'].str.lower() == 'eligible').astype(int)
    
    # Encoder les variables catégorielles
    encoders = {}
    for col in X.select_dtypes(include=['object']):
        print(f"\nValeurs uniques pour {col}:")
        print(sorted(X[col].unique()))
        encoders[col] = LabelEncoder()
        X[col] = encoders[col].fit_transform(X[col].astype(str))
        print(f"Classes encodées pour {col}:")
        print(sorted(encoders[col].classes_))
    
    # Diviser les données
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entraîner le modèle
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Évaluer le modèle
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Score d'entraînement : {train_score:.3f}")
    print(f"Score de test : {test_score:.3f}")
    
    # Créer le dossier models s'il n'existe pas
    models_dir = os.path.dirname(__file__)
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    # Sauvegarder le modèle et les encodeurs
    model_data = {
        'model': model,
        'encoders': encoders,
        'features': features
    }
    model_path = os.path.join(models_dir, 'eligibility_model.joblib')
    joblib.dump(model_data, model_path)
    
    print(f"Modèle et encodeurs sauvegardés dans {model_path}")

if __name__ == "__main__":
    train_eligibility_model()
