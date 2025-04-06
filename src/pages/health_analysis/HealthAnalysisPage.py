import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from ...services.data.DataService import DataService

class HealthAnalysisPage:
    def __init__(self):
        self.data_service = DataService()

    def init_callbacks(self, app):
        @app.callback(
            Output('health-location-filter', 'options'),
            Input('health-location-filter', 'search_value')
        )
        def update_location_options(search):
            df = self.data_service.get_donor_data()
            locations = sorted(df['arrondissement_de_residence'].unique())
            return [{'label': loc, 'value': loc} for loc in locations]
        
        @app.callback(
            [Output('detailed-stats', 'children'),
             Output('top-health-issues', 'figure'),
             Output('top-unavailability-reasons', 'figure'),
             Output('temporary-unavailability-chart', 'figure'),
             Output('geographic-health-analysis', 'figure'),
             Output('health-issues-chart', 'figure'),
             ],
            [Input('health-location-filter', 'value'),
             Input('health-date-range', 'start_date'),
             Input('health-date-range', 'end_date')]
        )
        def update_health_analysis(location, start_date, end_date):
            try:
                df = self.data_service.get_donor_data()
                df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
                
                # Définir les colonnes pour chaque catégorie
                health_cols = [col for col in df.columns if 'raison_de_non-eligibilité_totale__' in col]
                temp_unavail_cols = [col for col in df.columns if 'raison_indisponibilité__' in col]
                raisons_femmes = [col for col in df.columns if "raison_de_l'indisponibilité_de_la_femme_" in col]
                
                # Appliquer les filtres
                if location:
                    df = df[df['arrondissement_de_residence'] == location]
                if start_date:
                    df = df[df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()]
                if end_date:
                    df = df[df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()]
                
                # 1. Statistiques détaillées
                total = len(df)
                eligible = (df['eligibilite_au_don'] == 'eligible').sum()
                temp_unavailable = df[temp_unavail_cols + raisons_femmes].eq('oui').any(axis=1).sum()
                non_eligible = df[health_cols].eq('oui').any(axis=1).sum()
                
                # Calculer les pourcentages
                pct_eligible = (eligible / total) * 100 if total > 0 else 0
                pct_temp = (temp_unavailable / total) * 100 if total > 0 else 0
                pct_non = (non_eligible / total) * 100 if total > 0 else 0
                
                """detailed_stats = html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.H4("Donneurs éligibles", className="h6"),
                            html.P(f"{eligible} ({pct_eligible:.1f}%)", className="h3 text-primary")
                        ], width=4),
                        dbc.Col([
                            html.H4("Temporairement non disponible", className="h6"),
                            html.P(f"{temp_unavailable} ({pct_temp:.1f}%)", className="h3 text-danger")
                        ], width=4),
                        dbc.Col([
                            html.H4("Non éligibles", className="h6"),
                            html.P(f"{non_eligible} ({pct_non:.1f}%)", className="h3 text-warning")
                        ], width=4)
                    ])
                ])"""
                detailed_stats = html.Div([


                                        dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardBody([
                                                html.H4("Donneurs éligibles", className="h7"),
                                                html.P(f"{eligible} ({pct_eligible:.1f}%)", className="h4 text-primary")
                                            ])
                                        ], className="stat-card")
                                    ], md=4),
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardBody([
                                                html.H4("Temporairement non disponible", className="h7"),
                                                html.P(f"{temp_unavailable} ({pct_temp:.1f}%)", className="h4 text-danger")
                                            ])
                                        ], className="stat-card")
                                    ], md=4),
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardBody([
                                                html.H4("Non éligibles", className="h7"),
                                                html.P(f"{non_eligible} ({pct_non:.1f}%)", className="h4 text-warning")
                                            ])
                                        ], className="stat-card")
                                    ], md=4)
                                ], className="mb-4"),
                    ])
                
            
                # 2. Top problèmes de santé
                health_issues = []
                for col in health_cols:
                    count = (df[col] == 'oui').sum()
                    if count > 0:
                        issue = col.split('__')[-1].replace('[', '').replace(']', '').replace('_', ' ')
                        health_issues.append({'issue': issue, 'count': count})
                
                health_df = pd.DataFrame(health_issues)
                if not health_df.empty:
                    health_df = health_df.sort_values('count', ascending=False)
                    
                    top_health_fig = px.bar(
                        health_df.head(3),
                        x='issue',
                        y='count',
                        title="Principaux problèmes de santé",
                        labels={'issue': 'Problème de santé', 'count': 'Nombre de cas'},
                        color='count',
                        color_continuous_scale=['#8B0000', '#000000']
                    )
                    top_health_fig.update_layout(
                        showlegend=False,
                        xaxis_tickangle=-45,
                        margin=dict(l=0, r=0, t=40, b=100),
                        height=300
                    )
                else:
                    top_health_fig = go.Figure()
                
                # 3. Top raisons d'indisponibilité
                unavail_reasons = []
                for col in temp_unavail_cols + raisons_femmes:
                    count = (df[col] == 'oui').sum()
                    if count > 0:
                        reason = col.split('__')[-1].replace('[', '').replace(']', '').replace('_', ' ')
                        unavail_reasons.append({'reason': reason, 'count': count})
                
                unavail_df = pd.DataFrame(unavail_reasons)
                if not unavail_df.empty:
                    unavail_df = unavail_df.sort_values('count', ascending=False)
                    
                    top_unavail_fig = px.bar(
                        unavail_df.head(3),
                        x='reason',
                        y='count',
                        title="Principales raisons d'indisponibilité",
                        labels={'reason': 'Raison', 'count': 'Nombre de cas'},
                        color='count',
                        color_continuous_scale=['#8B0000', '#000000']
                    )
                    top_unavail_fig.update_layout(
                        showlegend=False,
                        xaxis_tickangle=-45,
                        margin=dict(l=0, r=0, t=40, b=100),
                        height=300
                    )
                else:
                    top_unavail_fig = go.Figure()
                
                # 4. Graphique d'indisponibilité temporaire
                temp_fig = px.bar(
                    unavail_df,
                    x='count',
                    y='reason',
                    orientation='h',
                    title="Raisons d'indisponibilité temporaire",
                    labels={'reason': 'Raison', 'count': 'Nombre de cas'},
                    color='count',
                    color_continuous_scale=['#8B0000', '#000000']
                )
                temp_fig.update_layout(
                    showlegend=False,
                    margin=dict(l=0, r=0, t=40, b=0),
                    height=400
                )
                
                # 5. Analyse géographique
                geo_stats = df.groupby('arrondissement_de_residence').agg({
                    'eligibilite_au_don': lambda x: (x != 'eligible').sum(),
                    'date_de_remplissage': 'count'
                }).reset_index()
                
                geo_stats.columns = ['arrondissement', 'non_eligible', 'total']
                geo_stats['pourcentage'] = (geo_stats['non_eligible'] / geo_stats['total'] * 100).round(1)
                geo_stats = geo_stats.sort_values('non_eligible', ascending=True)
                
                # Exclure les valeurs non précisées
                geo_stats = geo_stats[~geo_stats['arrondissement'].str.contains('pas précisé', case=False, na=False)]
                
                geo_fig = px.bar(
                    geo_stats,
                    x='non_eligible',
                    y='arrondissement',
                    orientation='h',
                    title="Cas d'inéligibilité par zone",
                    text=geo_stats['pourcentage'].apply(lambda x: f'{x}%'),
                    color='non_eligible',
                    color_continuous_scale=['#8B0000', '#000000']
                )
                geo_fig.update_layout(
                    showlegend=False,
                    margin=dict(l=0, r=0, t=40, b=0),
                    height=400,
                    xaxis_title="Nombre de cas",
                    yaxis_title="Arrondissement"
                )
                
                # 6. Graphique détaillé des problèmes de santé
                health_fig = px.bar(
                    health_df,
                    x='count',
                    y='issue',
                    orientation='h',
                    title="Détail des problèmes de santé",
                    labels={'issue': 'Problème', 'count': 'Nombre de cas'},
                    color='count',
                    color_continuous_scale=['#8B0000', '#000000']
                )
                health_fig.update_layout(
                    showlegend=False,
                    margin=dict(l=0, r=0, t=40, b=0),
                    height=400
                )
                
                # 7. Tableau d'interprétation
                interpretation_table = dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Indicateur"),
                            html.Th("Valeur"),
                            html.Th("Interprétation")
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td("Taux d'éligibilité"),
                            html.Td(f"{pct_eligible:.1f}%"),
                            html.Td("Pourcentage de donneurs éligibles au don")
                        ]),
                        html.Tr([
                            html.Td("Taux d'indisponibilité temporaire"),
                            html.Td(f"{pct_temp:.1f}%"),
                            html.Td("Pourcentage de donneurs temporairement indisponibles")
                        ]),
                        html.Tr([
                            html.Td("Taux d'inéligibilité"),
                            html.Td(f"{pct_non:.1f}%"),
                            html.Td("Pourcentage de donneurs non éligibles")
                        ])
                    ])
                ], bordered=True, hover=True, className="interpretation-table")
                
                return (
                    detailed_stats,
                    top_health_fig,
                    top_unavail_fig,
                    temp_fig,
                    geo_fig,
                    health_fig
                )
                
            except Exception as e:
                print(f"Erreur dans update_health_analysis: {str(e)}")
                return (
                    html.Div("Erreur lors du chargement des données"),
                    go.Figure(),
                    go.Figure(),
                    go.Figure(),
                    go.Figure(),
                    go.Figure(),
                    html.Div("Erreur lors du chargement des données")
                )

    def render(self):
        """Rendu de la page d'analyse de santé"""
        return dbc.Container([
            # Filtres (position fixe, z-index élevé)
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H4("Filtres ", className="card-title mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Zone géographique", className="mb-2"),
                                    dcc.Dropdown(
                                        id='health-location-filter',
                                        placeholder="Sélectionner une zone",
                                        className="mb-3",
                                        style={'zIndex': 9999}
                                    )
                                ], md=6),
                                dbc.Col([
                                    html.Label("Période d'analyse", className="mb-2"),
                                    dcc.DatePickerRange(
                                        id='health-date-range',
                                        className="mb-3",
                                        style={'zIndex': 9999}
                                    )
                                ], md=6)
                            ])
                        ])
                    ])
                ])
            ], className="mb-4", style={'position': 'relative', 'zIndex': 1000}),

            # Statistiques détaillées en haut
            dbc.Card([
                dbc.CardHeader("Statistiques détaillées"),
                dbc.CardBody(id='detailed-stats')
            ], className="mb-4"),
            
            # Contenu principal
            dbc.Row([
                # Première colonne (plus petite)
                dbc.Col([
                    # Top 3 problèmes de santé
                    dbc.Card([
                        dbc.CardHeader("Top 3 des problèmes de santé"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='top-health-issues',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="mb-4"),
                    
                    # Top 3 raisons d'indisponibilité
                    dbc.Card([
                        dbc.CardHeader("Top 3 des raisons d'indisponibilité"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='top-unavailability-reasons',
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ], width=4),
                
                # Deuxième colonne (plus grande)
                dbc.Col([
                    # Raisons d'indisponibilité temporaire
                    dbc.Card([
                        dbc.CardHeader("Raisons d'indisponibilité temporaire"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='temporary-unavailability-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="mb-4"),
                    
                    # Analyse par zone géographique
                    dbc.Card([
                        dbc.CardHeader("Analyse par zone géographique"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='geographic-health-analysis',
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ], width=8)
            ],  className="retention-container"),
            
            # Graphique des problèmes de santé en bas
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Problèmes de santé - Non éligibilité"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='health-issues-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ])
            ], className="chart-card mb-4"),
            
            
        ], fluid=True)
