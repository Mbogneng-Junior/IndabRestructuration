from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
from datetime import datetime
import numpy as np
import os
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Prédiction d'Éligibilité au Don de Sang",
    description="API pour prédire l'éligibilité d'un donneur potentiel",
    version="1.0.0"
)

# Charger le modèle
model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'eligibility_model.joblib')
model_data = joblib.load(model_path)
model = model_data['model']
encoders = model_data['encoders']
required_features = model_data['features']

print("Features requises par le modèle:", required_features)

# Définir le schéma des données d'entrée
class DonorData(BaseModel):
    age: int
    genre: str
    niveau_d_etude: str
    situation_matrimoniale: str
    profession: str
    religion: str
    a_deja_donne: bool
    date_dernier_don: str = None

class PredictionResponse(BaseModel):
    prediction: bool
    probability: float

@app.post("/predict", response_model=PredictionResponse)
async def predict_eligibility(data: DonorData):
    try:
        logger.info(f"Réception des données : {data.dict()}")
        
        # Préparer les données avec toutes les features requises
        input_data = {
            'age': data.age,
            'genre': data.genre,
            'niveau_d_etude': data.niveau_d_etude,
            'situation_matrimoniale_(sm)': data.situation_matrimoniale,
            'profession': data.profession,
            'religion': data.religion,
            'a_t_il_elle_deja_donne_le_sang': 'oui' if data.a_deja_donne else 'non'
        }
        
        # Vérifier que toutes les features requises sont présentes
        missing_features = [f for f in required_features if f not in input_data]
        if missing_features:
            raise ValueError(f"Features manquantes : {missing_features}")
        
        # Créer un DataFrame avec les bonnes colonnes dans le bon ordre
        input_df = pd.DataFrame([input_data])[required_features]
        
        # Encoder les variables catégorielles
        for col, encoder in encoders.items():
            if col in input_df.columns:
                try:
                    input_df[col] = encoder.transform(input_df[col].astype(str))
                except ValueError as e:
                    logger.error(f"Erreur d'encodage pour {col}: {str(e)}")
                    raise ValueError(f"Valeur invalide pour {col}: {input_df[col].iloc[0]}")
        
        logger.info(f"Features préparées : {input_df.to_dict(orient='records')[0]}")
        
        # Faire la prédiction
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        logger.info(f"Prédiction obtenue : {bool(prediction)} avec une probabilité de {float(probability)}")
        
        return {
            "prediction": bool(prediction),
            "probability": float(probability)
        }

    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
