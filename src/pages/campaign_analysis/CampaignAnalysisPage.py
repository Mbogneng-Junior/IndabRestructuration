import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from ...services.data.DataService import DataService

class CampaignAnalysisPage:
    def __init__(self):
        self.data_service = DataService()

    def init_callbacks(self, app):
        from dash.dependencies import Input, Output, State
        
        @app.callback(
            [Output("evolution-chart", "figure"),
             Output("density-chart", "figure"),
             Output("gender-eligible-chart", "figure"),
             Output("gender-donor-chart", "figure"),
             Output("gender-ratio-homme-chart", "figure"),
             Output("gender-ratio-femme-chart", "figure")],
            [Input("city-filter", "value"),
             Input("district-filter", "value"),
             Input("neighborhood-filter", "value"),
             Input("date-range", "start_date"),
             Input("date-range", "end_date")]
        )
        def update_charts(city, district, neighborhood, start_date, end_date):
            # Charger les données
            df_eligible = pd.read_csv('data/processed_data.csv')
            df_donneurs = pd.read_csv('data/data_cleaned.csv')
            
            # Convertir les dates
            df_eligible['date_de_remplissage'] = pd.to_datetime(df_eligible['date_de_remplissage'])
            df_donneurs['date'] = pd.to_datetime(df_donneurs['date'])
            
            # Filtrer par date si spécifié
            if start_date and end_date:
                mask_eligible = (df_eligible['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()) & \
                              (df_eligible['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date())
                df_eligible = df_eligible[mask_eligible]
                
                mask_donneurs = (df_donneurs['date'].dt.date >= pd.to_datetime(start_date).date()) & \
                               (df_donneurs['date'].dt.date <= pd.to_datetime(end_date).date())
                df_donneurs = df_donneurs[mask_donneurs]

            # 1. Graphique d'évolution
            df_eligible_daily = df_eligible.groupby(df_eligible['date_de_remplissage'].dt.date).size().reset_index()
            df_eligible_daily.columns = ['date', 'count']
            
            df_donneurs_daily = df_donneurs.groupby(df_donneurs['date'].dt.date).size().reset_index()
            df_donneurs_daily.columns = ['date', 'count']

            fig_evolution = go.Figure()
            fig_evolution.add_trace(go.Scatter(
                x=df_eligible_daily['date'],
                y=df_eligible_daily['count'],
                name='Personnes éligibles',
                line=dict(color='#1a1f3c', width=2)
            ))
            fig_evolution.add_trace(go.Scatter(
                x=df_donneurs_daily['date'],
                y=df_donneurs_daily['count'],
                name='Donneurs effectifs',
                line=dict(color='#c62828', width=2)
            ))
            fig_evolution.update_layout(
                title=None,
                xaxis_title="Date",
                yaxis_title="Nombre de personnes",
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#1a1f3c'},
                margin=dict(l=50, r=20, t=30, b=30),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            # 2. Courbe de densité pour l'âge
            fig_density = go.Figure()
            df_eligible_filtered = df_eligible[df_eligible['eligibilite_au_don'] == 'eligible']
            
            fig_density.add_trace(go.Histogram(
                x=df_eligible_filtered['age'],
                name='Personnes éligibles',
                histnorm='probability density',
                nbinsx=30,
                marker_color='#1a1f3c'
            ))
            
            fig_density.add_trace(go.Histogram(
                x=df_donneurs['age'],
                name='Donneurs effectifs',
                histnorm='probability density',
                nbinsx=30,
                marker_color='#c62828'
            ))
            
            fig_density.update_layout(
                title=None,
                xaxis_title="Âge",
                yaxis_title="Densité",
                barmode='overlay',
                bargap=0.1,
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#1a1f3c'},
                margin=dict(l=50, r=20, t=30, b=30),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            # 3. Diagrammes circulaires pour les proportions par genre
            # Pour les personnes éligibles
            hommes_eligible = len(df_eligible_filtered[df_eligible_filtered['genre'] == 'Homme'])
            femmes_eligible = len(df_eligible_filtered[df_eligible_filtered['genre'] == 'Femme'])
            total_eligible = hommes_eligible + femmes_eligible
            
            fig_genre_eligible = go.Figure(data=[go.Pie(
                labels=['Hommes', 'Femmes'],
                values=[hommes_eligible/total_eligible*100, femmes_eligible/total_eligible*100],
                hole=.3,
                marker_colors=['#1a1f3c', '#c62828']
            )])
            fig_genre_eligible.update_layout(
                title=None,
                height=300,
                showlegend=True,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            # Pour les donneurs effectifs
            hommes_donneurs = len(df_donneurs[df_donneurs['genre'] == 'Homme'])
            femmes_donneurs = len(df_donneurs[df_donneurs['genre'] == 'Femme'])
            total_donneurs = hommes_donneurs + femmes_donneurs
            
            fig_genre_donneurs = go.Figure(data=[go.Pie(
                labels=['Hommes', 'Femmes'],
                values=[hommes_donneurs/total_donneurs*100, femmes_donneurs/total_donneurs*100],
                hole=.3,
                marker_colors=['#1a1f3c', '#c62828']
            )])
            fig_genre_donneurs.update_layout(
                title=None,
                height=300,
                showlegend=True,
                margin=dict(l=20, r=20, t=30, b=20)
            )

            # 4. Diagrammes circulaires pour les ratios par genre
            # Pour les hommes
            ratio_hommes_eligible =  (hommes_eligible /hommes_donneurs) * 100
            fig_ratio_hommes = go.Figure(data=[go.Pie(
                labels=['Donneurs', 'Non donneurs'],
                values=[ratio_hommes_eligible, 100-ratio_hommes_eligible],
                hole=.3,
                marker_colors=['#1a1f3c', '#c62828']
            )])
            fig_ratio_hommes.update_layout(
                title=None,
                height=300,
                showlegend=True,
                margin=dict(l=20, r=20, t=30, b=20)
            )

            # Pour les femmes
            ratio_femmes_eligible =   (femmes_eligible /femmes_donneurs) * 100
            fig_ratio_femmes = go.Figure(data=[go.Pie(
                labels=['Donneuses', 'Non donneuses'],
                values=[ratio_femmes_eligible, 100-ratio_femmes_eligible],
                hole=.3,
                marker_colors=['#1a1f3c', '#c62828']
            )])
            fig_ratio_femmes.update_layout(
                title=None,
                height=300,
                showlegend=True,
                margin=dict(l=20, r=20, t=30, b=20)
            )

            return fig_evolution, fig_density, fig_genre_eligible, fig_genre_donneurs, fig_ratio_hommes, fig_ratio_femmes

    def render(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Analyse des Campagnes", className="mb-4 text-black")
                ])
            ]),
            
            # Filtres
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Filtres", className="card-title"),
                            dbc.Row([
                                dbc.Col([
                                  dbc.Label("Ville"),
                                  dcc.Dropdown(
                                    id='city-filter',
                                    options=[
                                        {'label': 'Toutes les villes', 'value': 'all'},
                                        {'label': 'Douala', 'value': 'douala'},
                                        {'label': 'Yaoundé', 'value': 'yaounde'}
                                    ],
                                    value='all',
                                    className="mb-3"
                                ),]),
                                dbc.Col([
                                    dbc.Label("Arrondissement"),
                                    dcc.Dropdown(
                                        id='district-filter',
                                        options=[],
                                        className="mb-3"
                                    ),
                                    ]),
                                dbc.Col([
                                    dbc.Label("Quartier"),
                                    dcc.Dropdown(
                                        id='neighborhood-filter',
                                        options=[],
                                        className="mb-3"
                                    ),
                                    ]),
                                dbc.Col([
                                    dbc.Label("Période"),
                                    dcc.DatePickerRange(
                                        id='date-range',
                                        display_format="DD/MM/YYYY",
                                        className="mb-3"
                                    )
                                ]),
                            ])
                        ])
                    ], className="mb-4")
                ])
            ]),
            
            # Graphiques d'évolution et de densité
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Évolution temporelle des inscriptions et des dons"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="evolution-chart",
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card mb-4")
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribution de l'âge des personnes éligibles et des donneurs"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="density-chart",
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card mb-4")
                ])
            ]),
            
            # Première ligne de diagrammes circulaires
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Répartition des personnes éligibles par genre"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="gender-eligible-chart",
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Répartition des donneurs effectifs par genre"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="gender-donor-chart",
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ], md=6)
            ], className="chart-card mb-4"),
            
            # Deuxième ligne de diagrammes circulaires
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Proportion des hommes éligibles ayant donné"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="gender-ratio-homme-chart",
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ], className="chart-card mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Proportion des femmes éligibles ayant donné"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="gender-ratio-femme-chart",
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ], className="chart-card mb-4")
            ])
        ], fluid=True)
