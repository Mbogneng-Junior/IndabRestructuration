import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import requests
from ...services.data.DataService import DataService

class PredictionPage:
    def __init__(self):
        self.data_service = DataService()

    def init_callbacks(self, app):
        @app.callback(
            [Output('prediction-result', 'children'),
             Output('prediction-probability', 'children')],
            [Input('predict-button', 'n_clicks')],
            [State('age-input', 'value'),
             State('gender-input', 'value'),
             State('education-input', 'value'),
             State('marital-input', 'value'),
             State('profession-input', 'value'),
             State('religion-input', 'value'),
             State('has-donated', 'value')]
        )
        def predict_eligibility(n_clicks, age, gender, education, marital, profession, religion, has_donated):
            if n_clicks is None:
                return "", "Cette prédiction est basée sur un modèle d'apprentissance automatique et ne remplace pas l'avis d'un professionnel de santé."
            
            try:
                # Vérifier que toutes les valeurs sont présentes
                if None in [age, gender, education, marital, profession, religion] or not age or not profession:
                    return (
                        html.Div([
                            html.H4("Veuillez remplir tous les champs", className="text-warning"),
                            html.P("Tous les champs sont obligatoires pour faire une prédiction.")
                        ]),
                        ""
                    )
                
                # Préparer les données pour l'API
                # Standardiser les valeurs
                gender = str(gender) if gender else "Femme"  
                education = str(education) if education else "Pas Précisé"
                marital = str(marital) if marital else "Célibataire"
                profession = str(profession).lower() if profession else "pas precisé"
                religion = str(religion).lower() if religion else "pas précisé"

                data = {
                    "age": int(age),
                    "genre": gender,
                    "niveau_d_etude": education,
                    "situation_matrimoniale": marital,
                    "profession": profession,
                    "ville": "douala",  
                    "arrondissement_de_residence": "douala 1",  
                    "nationalite": "camerounaise",  
                    "religion": religion,
                    "a_deja_donne": has_donated == "Oui",
                    "date_dernier_don": None
                }
                
                print("Données envoyées à l'API:", data)  
                
                # Faire la requête à l'API
                response = requests.post('http://localhost:8000/predict', json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Créer le message de résultat
                    if result['eligible']:
                        message = html.Div([
                            html.H4("Éligible au don de sang", className="text-success"),
                            html.P("Le modèle prédit que vous êtes éligible au don de sang.")
                        ])
                    else:
                        message = html.Div([
                            html.H4("Non éligible au don de sang", className="text-danger"),
                            html.P("Le modèle prédit que vous n'êtes pas éligible au don de sang.")
                        ])
                    
                    # Créer le message de probabilité
                    probability = f"Probabilité : {result['probability']:.1%}"
                    
                    return message, probability
                else:
                    print(f"Erreur API: {response.status_code} - {response.text}")  
                    return f"Erreur lors de la prédiction : {response.text}", "Probabilité : "
                    
            except Exception as e:
                print(f"Erreur lors de la prédiction : {str(e)}")  
                return f"Erreur lors de la prédiction : {str(e)}", "Probabilité : "

    def render(self):
        """Rendu de la page de prédiction d'éligibilité"""
        # Récupération des professions uniques
        professions = self.data_service.get_unique_professions()
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("Prédiction d'Éligibilité au Don de Sang", 
                            className="text-primary mb-4"),
                    html.P("Utilisez notre modèle d'IA pour prédire l'éligibilité d'un nouveau donneur",
                          className="text-muted mb-4")
                ])
            ]),
            
            dbc.Row([
                # Formulaire de prédiction
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Informations du Donneur"),
                        dbc.CardBody([
                            # Âge
                            dbc.Row([
                                dbc.Label("Âge", html_for="age-input", className="fw-bold mb-2"),
                                dbc.Input(
                                    id="age-input",
                                    type="number",
                                    min=18,
                                    max=65,
                                    step=1,
                                    placeholder="Entrez l'âge"
                                ),
                            ], className="mb-3"),
                            
                            # Genre
                            dbc.Row([
                                dbc.Label("Genre", html_for="gender-input", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="gender-input",
                                    options=[
                                        {"label": "Femme", "value": "Femme"},
                                        {"label": "Homme", "value": "Homme"}
                                    ],
                                    value="Femme",
                                    placeholder="Sélectionnez le genre"
                                ),
                            ], className="mb-3"),
                            
                            # Niveau d'études
                            dbc.Row([
                                dbc.Label("Niveau d'études", html_for="education-input", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="education-input",
                                    options=[
                                        {"label": "Primaire", "value": "Primaire"},
                                        {"label": "Secondaire", "value": "Secondaire"},
                                        {"label": "Universitaire", "value": "Universitaire"},
                                        {"label": "Pas Précisé", "value": "Pas Précisé"}
                                    ],
                                    placeholder="Sélectionnez le niveau d'études"
                                ),
                            ], className="mb-3"),
                            
                            # Situation matrimoniale
                            dbc.Row([
                                dbc.Label("Situation matrimoniale", html_for="marital-input", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="marital-input",
                                    options=[
                                        {"label": "Célibataire", "value": "Célibataire"},
                                        {"label": "Marié(e)", "value": "Marié (e)"},
                                        {"label": "Divorcé(e)", "value": "Divorcé(e)"},
                                        {"label": "Veuf/Veuve", "value": "Veuf (ve)"}
                                    ],
                                    placeholder="Sélectionnez la situation matrimoniale"
                                ),
                            ], className="mb-3"),
                            
                            # Profession
                            dbc.Row([
                                dbc.Label("Profession", html_for="profession-input", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="profession-input",
                                    options=[{"label": p, "value": p} for p in professions],
                                    placeholder="Sélectionnez la profession"
                                ),
                            ], className="mb-3"),
                            
                            # Religion
                            dbc.Row([
                                dbc.Label("Religion", html_for="religion-input", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="religion-input",
                                    options=[
                                        {"label": "Chrétien (Catholique)", "value": "chretien (catholique)"},
                                        {"label": "Chrétien (Protestant)", "value": "chretien (protestant)"},
                                        {"label": "Musulman", "value": "musulman"},
                                        {"label": "Autre", "value": "autre"},
                                        {"label": "Non précisé", "value": "pas précisé"}
                                    ],
                                    placeholder="Sélectionnez la religion"
                                ),
                            ], className="mb-3"),
                            
                            # A déjà donné
                            dbc.Row([
                                dbc.Label("A déjà donné le sang ?", html_for="has-donated", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="has-donated",
                                    options=[
                                        {"label": "Oui", "value": "Oui"},
                                        {"label": "Non", "value": "Non"}
                                    ],
                                    value="Non",
                                    placeholder="A déjà donné le sang ?"
                                ),
                            ], className="mb-3"),
                            
                            # Bouton de prédiction
                            dbc.Button(
                                "Prédire l'éligibilité",
                                id="predict-button",
                                color="primary",
                                className="w-100 mt-3"
                            )
                        ])
                    ], className="shadow-sm mb-4")
                ], md=6),
                
                # Résultat de la prédiction
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Résultat de la Prédiction"),
                        dbc.CardBody([
                            html.Div(id="prediction-result"),
                            html.Hr(),
                            html.P(id="prediction-probability", className="text-muted"),
                            html.P(
                                "Cette prédiction est basée sur un modèle d'apprentissage automatique "
                                "et ne remplace pas l'avis d'un professionnel de santé.",
                                className="text-muted small"
                            )
                        ])
                    ], className="h-100 shadow-sm")
                ], md=6)
            ])
        ], fluid=True, className="px-4 py-3")
