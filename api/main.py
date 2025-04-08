from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os
from typing import List, Optional
import numpy as np
from datetime import datetime

# Créer l'application FastAPI
app = FastAPI(
    title="API de Prédiction d'Éligibilité au Don de Sang",
    description="Cette API permet de prédire l'éligibilité d'un donneur au don de sang",
    version="1.0.0"
)

# Définir le modèle de données pour la requête
class DonorData(BaseModel):
    age: int
    genre: str
    niveau_d_etude: str
    situation_matrimoniale: str
    profession: str
    
    religion: str
    a_deja_donne: bool
    date_dernier_don: Optional[str] = None

# Charger le modèle et les encodeurs
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'eligibility_model.joblib')
if not os.path.exists(model_path):
    raise Exception(f"Le modèle n'existe pas à l'emplacement : {model_path}")

model_data = joblib.load(model_path)
model = model_data['model']
encoders = model_data['encoders']
features = model_data['features']

@app.get("/")
async def root():
    """Point de terminaison racine pour vérifier que l'API fonctionne"""
    return {
        "message": "API de Prédiction d'Éligibilité au Don de Sang",
        "status": "active",
        "version": "1.0.0"
    }

@app.post("/predict")
async def predict_eligibility(donor: DonorData):
    """Prédit l'éligibilité d'un donneur au don de sang"""
    try:
        # Préparer les données pour la prédiction
        features_dict = {
            'age': donor.age,
            'genre': donor.genre,
            'niveau_d_etude': donor.niveau_d_etude,
            'situation_matrimoniale_(sm)': donor.situation_matrimoniale,
            'profession': donor.profession.lower(),
            
            'religion': donor.religion.lower(),
            'a_t_il_elle_deja_donne_le_sang': 'oui' if donor.a_deja_donne else 'non'
        }
        
        features_df = pd.DataFrame([features_dict])
        print("Features avant prédiction:", features_df.to_dict())
        
        # Encoder les variables catégorielles
        for col in features_df.select_dtypes(include=['object']):
            if col in encoders:
                # Gérer les nouvelles catégories
                features_df[col] = features_df[col].astype(str)
                known_categories = set(encoders[col].classes_)
                if features_df[col].values[0] not in known_categories:
                    print(f"Valeur inconnue '{features_df[col].values[0]}' pour {col}, utilisation de la valeur par défaut '{encoders[col].classes_[0]}'")
                    features_df[col] = encoders[col].classes_[0]
                features_df[col] = encoders[col].transform(features_df[col])
        
        print("Features après encodage:", features_df.to_dict())
        
        # Faire la prédiction
        prediction = model.predict(features_df)[0]
        probability = model.predict_proba(features_df)[0].max()
        
        return {
            "eligible": bool(prediction),
            "probability": float(probability),
            "message": "Éligible au don de sang" if prediction else "Non éligible au don de sang"
        }
        
    except Exception as e:
        print(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Si vous exécutez ce fichier directement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
