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
             Output('prediction-explanation', 'children')],
            [Input('predict-button', 'n_clicks')],
            [State('age-input', 'value'),
             State('gender-dropdown', 'value'),
             State('education-dropdown', 'value'),
             State('marital-dropdown', 'value'),
             State('profession-dropdown', 'value'),
             State('religion-dropdown', 'value'),
             State('previous-donation-radio', 'value'),
             State('last-donation-date', 'date')]
        )
        def predict_eligibility(n_clicks, age, gender, education, marital_status, profession, religion, has_donated, last_donation):
            if n_clicks is None:
                return "", ""
            
            try:
                # Vérifier que toutes les valeurs requises sont présentes
                if None in [age, gender, education, marital_status, profession, religion]:
                    return html.Div([
                        html.H3("Données manquantes", className="text-warning"),
                        html.P("Veuillez remplir tous les champs obligatoires.")
                    ]), ""
                
                # Créer le dictionnaire avec les features requises
                data = {
                    'age': age,
                    'genre': gender,
                    'niveau_d_etude': education,
                    'situation_matrimoniale': marital_status,
                    'profession': profession,
                    'religion': religion.lower(),
                    'a_deja_donne': has_donated == 'True',
                    'date_dernier_don': last_donation
                }
                
                print("Données envoyées à l'API:", data)
                
                # Appel à l'API
                response = requests.post('http://localhost:8000/predict', json=data)
                response.raise_for_status()  # Lève une exception si le statut n'est pas 2xx
                
                result = response.json()
                if not isinstance(result, dict) or 'eligible' not in result or 'probability' not in result:
                    raise ValueError(f"Format de réponse invalide: {result}")
                
                prediction = result['eligible']
                probability = result['probability']
                
                # Formater le résultat
                if prediction:
                    result_text = html.Div([
                        html.H3("Éligible au don", className="text-success"),
                        html.P(f"Probabilité: {probability:.1%}"),
                        html.P(result.get('message', ''), className="text-muted")
                    ])
                    explanation = html.Div([
                        html.P("Le modèle prédit que cette personne est éligible pour le don de sang."),
                        html.P("Facteurs positifs probables:"),
                        html.Ul([
                            html.Li("Âge approprié"),
                            html.Li("Pas de contre-indications majeures")
                        ]),
                        html.Hr(),
                        html.P(
                            "Cette prédiction est basée sur un modèle d'apprentissage automatique "
                            "et ne remplace pas l'avis d'un professionnel de santé.",
                            className="text-muted small"
                        )
                    ])
                else:
                    result_text = html.Div([
                        html.H3("Non éligible au don", className="text-danger"),
                        html.P(f"Probabilité d'inéligibilité: {(1-probability):.1%}"),
                        html.P(result.get('message', ''), className="text-muted")
                    ])
                    explanation = html.Div([
                        html.P("Le modèle prédit que cette personne n'est pas éligible pour le don de sang."),
                        html.P("Raisons possibles:"),
                        html.Ul([
                            html.Li("Critères d'âge non satisfaits"),
                            html.Li("Délai insuffisant depuis le dernier don"),
                            html.Li("Autres facteurs de risque potentiels")
                        ]),
                        html.Hr(),
                        html.P(
                            "Cette prédiction est basée sur un modèle d'apprentissage automatique "
                            "et ne remplace pas l'avis d'un professionnel de santé.",
                            className="text-muted small"
                        )
                    ])
                
                return result_text, explanation
                
            except requests.exceptions.RequestException as e:
                print(f"Erreur de requête: {str(e)}")
                return html.Div([
                    html.H3("Erreur de connexion", className="text-danger"),
                    html.P("Impossible de contacter le serveur de prédiction."),
                    html.P(f"Détail: {str(e)}", className="text-muted small")
                ]), ""
            except ValueError as e:
                print(f"Erreur de données: {str(e)}")
                return html.Div([
                    html.H3("Erreur de données", className="text-danger"),
                    html.P("Format de données invalide."),
                    html.P(f"Détail: {str(e)}", className="text-muted small")
                ]), ""
            except Exception as e:
                print(f"Erreur: {str(e)}")
                return html.Div([
                    html.H3("Erreur", className="text-danger"),
                    html.P("Une erreur s'est produite lors de la prédiction."),
                    html.P(f"Détail: {str(e)}", className="text-muted small")
                ]), ""

    def render(self):
        """Rendu de la page de prédiction d'éligibilité"""
        # Récupération des professions uniques
        professions = self.data_service.get_unique_professions()
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Prédiction d'Éligibilité au Don de Sang", 
                            className="text-black mb-4"),
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
                                dbc.Label("Genre", html_for="gender-dropdown", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="gender-dropdown",
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
                                dbc.Label("Niveau d'études", html_for="education-dropdown", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="education-dropdown",
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
                                dbc.Label("Situation matrimoniale", html_for="marital-dropdown", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="marital-dropdown",
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
                                dbc.Label("Profession", html_for="profession-dropdown", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="profession-dropdown",
                                    options=[{"label": p, "value": p} for p in professions],
                                    placeholder="Sélectionnez la profession"
                                ),
                            ], className="mb-3"),
                            
                            # Ville
                            dbc.Row([
                                dbc.Label("Ville", html_for="ville-dropdown", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="ville-dropdown",
                                    options=[
                                        {"label": "Douala", "value": "Douala"},
                                        {"label": "Yaoundé", "value": "Yaoundé"},
                                        {"label": "Bamenda", "value": "Bamenda"},
                                        {"label": "Bafoussam", "value": "Bafoussam"}
                                    ],
                                    value="Douala",
                                    placeholder="Sélectionnez la ville"
                                ),
                            ], className="mb-3"),
                            
                            # Arrondissement de résidence
                            dbc.Row([
                                dbc.Label("Arrondissement de résidence", html_for="arrondissement-dropdown", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="arrondissement-dropdown",
                                    options=[
                                        {"label": "Douala 1", "value": "Douala 1"},
                                        {"label": "Douala 2", "value": "Douala 2"},
                                        {"label": "Douala 3", "value": "Douala 3"},
                                        {"label": "Douala 4", "value": "Douala 4"}
                                    ],
                                    value="Douala 1",
                                    placeholder="Sélectionnez l'arrondissement de résidence"
                                ),
                            ], className="mb-3"),
                            
                            # Nationalité
                            dbc.Row([
                                dbc.Label("Nationalité", html_for="nationalite-dropdown", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="nationalite-dropdown",
                                    options=[
                                        {"label": "Camerounaise", "value": "Camerounaise"},
                                        {"label": "Française", "value": "Française"},
                                        {"label": "Anglaise", "value": "Anglaise"},
                                        {"label": "Autre", "value": "Autre"}
                                    ],
                                    value="Camerounaise",
                                    placeholder="Sélectionnez la nationalité"
                                ),
                            ], className="mb-3"),
                            
                            # Religion
                            dbc.Row([
                                dbc.Label("Religion", html_for="religion-dropdown", className="fw-bold mb-2"),
                                dbc.Select(
                                    id="religion-dropdown",
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
                                dbc.Label("A déjà donné le sang ?", html_for="previous-donation-radio", className="fw-bold mb-2"),
                                dbc.RadioItems(
                                    id="previous-donation-radio",
                                    options=[
                                        {"label": "Oui", "value": "True"},
                                        {"label": "Non", "value": "False"}
                                    ],
                                    value="False",
                                    inline=True
                                ),
                            ], className="mb-3"),
                            
                            # Date du dernier don
                            dbc.Row([
                                dbc.Label("Date du dernier don", html_for="last-donation-date", className="fw-bold mb-2"),
                                dcc.DatePickerSingle(
                                    id="last-donation-date",
                                    placeholder="Sélectionnez la date"
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
                            html.Div(id="prediction-explanation")
                        ])
                    ], className="h-100 shadow-sm")
                ], md=6)
            ])
        ], fluid=True, className="px-4 py-3")
