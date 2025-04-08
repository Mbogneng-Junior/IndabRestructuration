import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import pandas as pd
import numpy as np
from textblob import TextBlob
import os
from ...services.data.DataService import DataService

class FeedbackPage:
    def __init__(self):
        self.data_service = DataService()

    def init_callbacks(self, app):
        @app.callback(
            [Output('total-feedback', 'children'),
             Output('positive-feedback', 'children'),
             Output('negative-feedback', 'children'),
             Output('feedback-pie-chart', 'figure')],
            [Input('feedback-date-range', 'start_date'),
             Input('feedback-date-range', 'end_date')]
        )
        def update_feedback_stats(start_date, end_date):
            try:
                df = self.data_service.get_donor_data()
                df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
                
                # Appliquer les filtres de date
                mask = pd.Series(True, index=df.index)
                if start_date:
                    mask &= df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()
                if end_date:
                    mask &= df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()
                
                df_filtered = df[mask]
                
                # Calculer les statistiques
                total_feedback = len(df_filtered)
                positive_feedback = len(df_filtered[df_filtered['eligibilite_au_don'].str.lower() == 'eligible'])
                negative_feedback = total_feedback - positive_feedback
                
                # Créer le graphique en camembert
                pie_data = pd.DataFrame({
                    'Type': ['Éligibles', 'Non éligibles'],
                    'Nombre': [positive_feedback, negative_feedback]
                })
                
                pie_fig = px.pie(
                    pie_data,
                    values='Nombre',
                    names='Type',
                    title="Répartition des retours",
                    color_discrete_sequence=['#1a1f3c', '#c62828']
                )
                pie_fig.update_layout(showlegend=True)
                
                return (
                    f"{total_feedback:,}",
                    f"{positive_feedback:,}",
                    f"{negative_feedback:,}",
                    pie_fig
                )
                
            except Exception as e:
                print(f"Erreur dans update_feedback_stats: {str(e)}")
                empty_fig = go.Figure()
                empty_fig.update_layout(
                    title="Aucune donnée disponible",
                    annotations=[dict(
                        text=str(e),
                        xref="paper",
                        yref="paper",
                        showarrow=False,
                        font=dict(size=14)
                    )]
                )
                return "0", "0", "0", empty_fig
        
        @app.callback(
            Output('feedback-timeline', 'figure'),
            [Input('feedback-date-range', 'start_date'),
             Input('feedback-date-range', 'end_date')]
        )
        def update_feedback_timeline(start_date, end_date):
            try:
                df = self.data_service.get_donor_data()
                df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
                
                # Appliquer les filtres de date
                mask = pd.Series(True, index=df.index)
                if start_date:
                    mask &= df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()
                if end_date:
                    mask &= df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()
                
                df_filtered = df[mask]
                
                # Calculer les statistiques mensuelles
                monthly_stats = df_filtered.groupby(pd.Grouper(key='date_de_remplissage', freq='M')).agg({
                    'eligibilite_au_don': lambda x: (x.str.lower() == 'eligible').mean()
                }).reset_index()
                
                # Convertir en pourcentage
                monthly_stats['eligibilite_au_don'] = monthly_stats['eligibilite_au_don'] * 100
                
                fig = px.line(
                    monthly_stats,
                    x='date_de_remplissage',
                    y='eligibilite_au_don',
                    title="Évolution du taux d'éligibilité",
                    labels={
                        'date_de_remplissage': 'Date',
                        'eligibilite_au_don': "Taux d'éligibilité (%)"
                    }
                )
                
                fig.update_layout(
                    showlegend=False,
                    xaxis_title="Période",
                    yaxis_title="Taux d'éligibilité (%)",
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                return fig
                
            except Exception as e:
                print(f"Erreur dans update_feedback_timeline: {str(e)}")
                empty_fig = go.Figure()
                empty_fig.update_layout(
                    title="Aucune donnée disponible",
                    annotations=[dict(
                        text=str(e),
                        xref="paper",
                        yref="paper",
                        showarrow=False,
                        font=dict(size=14)
                    )]
                )
                return empty_fig
        
        @app.callback(
            [Output('age-feedback-analysis', 'figure'),
             Output('gender-feedback-analysis', 'figure'),
             Output('education-feedback-analysis', 'figure'),
             Output('location-feedback-analysis', 'figure')],
            [Input('feedback-date-range', 'start_date'),
             Input('feedback-date-range', 'end_date')]
        )
        def update_feedback_analysis(start_date, end_date):
            try:
                df = self.data_service.get_donor_data()
                df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
                
                # Appliquer les filtres de date
                mask = pd.Series(True, index=df.index)
                if start_date:
                    mask &= df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()
                if end_date:
                    mask &= df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()
                
                df_filtered = df[mask]
                
                # Créer les tranches d'âge
                df_filtered['age'] = pd.to_numeric(df_filtered['age'], errors='coerce')
                df_filtered['age'] = df_filtered['age'].fillna(30)
                df_filtered['age'] = df_filtered['age'].clip(lower=18, upper=100)
                bins = [0, 25, 35, 45, 55, float('inf')]
                labels = ['18-25', '26-35', '36-45', '46-55', '56+']
                df_filtered['tranche_age'] = pd.cut(df_filtered['age'], bins=bins, labels=labels)
                
                # Analyse par âge
                age_stats = df_filtered.groupby('tranche_age').agg({
                    'eligibilite_au_don': lambda x: (x.str.lower() == 'eligible').mean() * 100
                }).reset_index()
                
                age_fig = px.bar(
                    age_stats,
                    x='tranche_age',
                    y='eligibilite_au_don',
                    title="Taux d'éligibilité par tranche d'âge",
                    labels={
                        'tranche_age': "Tranche d'âge",
                        'eligibilite_au_don': "Taux d'éligibilité (%)"
                    }
                )
                
                # Analyse par genre
                gender_stats = df_filtered.groupby('genre').agg({
                    'eligibilite_au_don': lambda x: (x.str.lower() == 'eligible').mean() * 100
                }).reset_index()
                
                gender_fig = px.bar(
                    gender_stats,
                    x='genre',
                    y='eligibilite_au_don',
                    title="Taux d'éligibilité par genre",
                    labels={
                        'genre': 'Genre',
                        'eligibilite_au_don': "Taux d'éligibilité (%)"
                    }
                )
                
                # Analyse par niveau d'études
                education_stats = df_filtered.groupby('niveau_d_etude').agg({
                    'eligibilite_au_don': lambda x: (x.str.lower() == 'eligible').mean() * 100
                }).reset_index()
                
                education_fig = px.bar(
                    education_stats,
                    x='niveau_d_etude',
                    y='eligibilite_au_don',
                    title="Taux d'éligibilité par niveau d'études",
                    labels={
                        'niveau_d_etude': "Niveau d'études",
                        'eligibilite_au_don': "Taux d'éligibilité (%)"
                    }
                )
                
                # Analyse par localisation
                location_stats = df_filtered.groupby('arrondissement_de_residence').agg({
                    'eligibilite_au_don': lambda x: (x.str.lower() == 'eligible').mean() * 100
                }).reset_index()
                
                location_fig = px.bar(
                    location_stats,
                    x='arrondissement_de_residence',
                    y='eligibilite_au_don',
                    title="Taux d'éligibilité par arrondissement",
                    labels={
                        'arrondissement_de_residence': 'Arrondissement',
                        'eligibilite_au_don': "Taux d'éligibilité (%)"
                    }
                )
                
                # Mettre à jour le layout de tous les graphiques
                for fig in [age_fig, gender_fig, education_fig, location_fig]:
                    fig.update_layout(
                        showlegend=False,
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                
                return age_fig, gender_fig, education_fig, location_fig
                
            except Exception as e:
                print(f"Erreur dans update_feedback_analysis: {str(e)}")
                empty_fig = go.Figure()
                empty_fig.update_layout(
                    title="Aucune donnée disponible",
                    annotations=[dict(
                        text=str(e),
                        xref="paper",
                        yref="paper",
                        showarrow=False,
                        font=dict(size=14)
                    )]
                )
                return empty_fig, empty_fig, empty_fig, empty_fig

    def render(self):
        """Rendu de la page d'analyse des retours"""
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Analyse des Retours", 
                            className="text-black mb-4"),
                    html.P("Analyse détaillée des retours et de la satisfaction des donneurs",
                          className="text-muted mb-4")
                ])
            ]),
            
            # Filtres
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Période d'analyse"),
                            dcc.DatePickerRange(
                                id='feedback-date-range',
                                start_date=date(2019, 1, 1),  # Ajusté pour correspondre aux données
                                end_date=date(2024, 12, 31),
                                display_format='DD/MM/YYYY',
                                className="mb-3"
                            )
                        ], md=12)
                    ])
                ])
            ], className="mb-4"),
            
            # Statistiques générales
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Retours totaux"),
                        dbc.CardBody([
                            html.H3(id="total-feedback", className="text-primary text-center"),
                            dbc.Spinner(color="primary", type="grow", size="sm")
                        ])
                    ])
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Retours positifs"),
                        dbc.CardBody([
                            html.H3(id="positive-feedback", className="text-success text-center"),
                            dbc.Spinner(color="success", type="grow", size="sm")
                        ])
                    ])
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Retours négatifs"),
                        dbc.CardBody([
                            html.H3(id="negative-feedback", className="text-danger text-center"),
                            dbc.Spinner(color="danger", type="grow", size="sm")
                        ])
                    ])
                ], md=4)
            ], className="mb-4"),
            
            # Graphiques d'analyse
            dbc.Row([
                # Graphique en camembert
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Répartition des retours"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(
                                    id='feedback-pie-chart',
                                    config={'displayModeBar': False}
                                ),
                                color="primary",
                                type="grow",
                                size="sm"
                            )
                        ])
                    ])
                ], md=6),
                
                # Timeline
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Évolution des retours dans le temps"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(
                                    id='feedback-timeline',
                                    config={'displayModeBar': False}
                                ),
                                color="primary",
                                type="grow",
                                size="sm"
                            )
                        ])
                    ])
                ], md=6)
            ], className="mb-4"),
            
            # Analyses croisées
            dbc.Row([
                # Colonne de gauche
                dbc.Col([
                    # Analyse par âge
                    dbc.Card([
                        dbc.CardHeader("Analyse par tranche d'âge"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(
                                    id='age-feedback-analysis',
                                    config={'displayModeBar': False}
                                ),
                                color="primary",
                                type="grow",
                                size="sm"
                            )
                        ])
                    ], className="mb-4"),
                    
                    # Analyse par genre
                    dbc.Card([
                        dbc.CardHeader("Analyse par genre"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(
                                    id='gender-feedback-analysis',
                                    config={'displayModeBar': False}
                                ),
                                color="primary",
                                type="grow",
                                size="sm"
                            )
                        ])
                    ])
                ], md=6),
                
                # Colonne de droite
                dbc.Col([
                    # Analyse par niveau d'études
                    dbc.Card([
                        dbc.CardHeader("Analyse par niveau d'études"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(
                                    id='education-feedback-analysis',
                                    config={'displayModeBar': False}
                                ),
                                color="primary",
                                type="grow",
                                size="sm"
                            )
                        ])
                    ], className="mb-4"),
                    
                    # Analyse par localisation
                    dbc.Card([
                        dbc.CardHeader("Analyse par localisation"),
                        dbc.CardBody([
                            dbc.Spinner(
                                dcc.Graph(
                                    id='location-feedback-analysis',
                                    config={'displayModeBar': False}
                                ),
                                color="primary",
                                type="grow",
                                size="sm"
                            )
                        ])
                    ])
                ], md=6)
            ])
        ], fluid=True)

class SentimentPage:
    def __init__(self):
        self.data_service = DataService()
        self.generate_feedback_data()

    def generate_feedback_data(self):
        # Générer des données de feedback synthétiques
        df = self.data_service.get_donor_data()
        n_samples = len(df)
        
        # Générer des feedbacks aléatoires
        feedbacks = []
        sentiments = []
        dates = []
        
        positive_feedbacks = [
            "Très satisfait du processus de don, personnel accueillant",
            "Excellente expérience, je reviendrai sûrement",
            "Service rapide et professionnel",
            "Équipe médicale très compétente",
            "Atmosphère rassurante et confortable"
        ]
        
        negative_feedbacks = [
            "Temps d'attente trop long",
            "Manque d'information sur le processus",
            "Local peu accessible",
            "Communication à améliorer",
            "Procédure trop complexe"
        ]
        
        neutral_feedbacks = [
            "Processus standard",
            "Service correct",
            "Rien de particulier à signaler",
            "Comme prévu",
            "Service normal"
        ]
        
        for _ in range(n_samples):
            if random.random() < 0.7:  # 70% ont donné un feedback
                sentiment = random.choice(['positif', 'négatif', 'neutre'])
                if sentiment == 'positif':
                    feedback = random.choice(positive_feedbacks)
                elif sentiment == 'négatif':
                    feedback = random.choice(negative_feedbacks)
                else:
                    feedback = random.choice(neutral_feedbacks)
            else:
                feedback = None
                sentiment = None
            
            feedbacks.append(feedback)
            sentiments.append(sentiment)
            dates.append(df['date_de_remplissage'].iloc[_])
        
        self.feedback_df = pd.DataFrame({
            'date': dates,
            'feedback': feedbacks,
            'sentiment': sentiments,
            'age': df['age'],
            'genre': df['genre']
        })

    def init_callbacks(self, app):
        @app.callback(
            [Output('sentiment-distribution', 'figure'),
             Output('sentiment-timeline', 'figure'),
             Output('sentiment-demographics', 'figure'),
             Output('feedback-stats', 'children')],
            [Input('date-range', 'start_date'),
             Input('date-range', 'end_date')]
        )
        def update_sentiment_analysis(start_date, end_date):
            df = self.feedback_df.copy()
            
            if start_date:
                df = df[df['date'].dt.date >= pd.to_datetime(start_date).date()]
            if end_date:
                df = df[df['date'].dt.date <= pd.to_datetime(end_date).date()]
            
            # Statistiques de participation
            total = len(df)
            avec_feedback = df['feedback'].notna().sum()
            sans_feedback = total - avec_feedback
            pct_participation = (avec_feedback / total) * 100 if total > 0 else 0
            
            # Distribution des sentiments
            sentiment_counts = df['sentiment'].value_counts()
            fig_distribution = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Distribution des sentiments",
                color_discrete_map={'positif': '#28a745', 'négatif': '#dc3545', 'neutre': '#ffc107'}
            )
            
            # Évolution temporelle
            timeline_df = df.groupby(['date', 'sentiment']).size().reset_index(name='count')
            fig_timeline = px.line(
                timeline_df,
                x='date',
                y='count',
                color='sentiment',
                title="Évolution des sentiments dans le temps",
                color_discrete_map={'positif': '#28a745', 'négatif': '#dc3545', 'neutre': '#ffc107'}
            )
            
            # Analyse démographique
            demo_df = df.groupby(['age', 'sentiment']).size().reset_index(name='count')
            fig_demographics = px.scatter(
                demo_df,
                x='age',
                y='count',
                color='sentiment',
                title="Distribution des sentiments par âge",
                color_discrete_map={'positif': '#28a745', 'négatif': '#dc3545', 'neutre': '#ffc107'}
            )
            
            # Statistiques de participation
            stats = html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Statistiques de participation", className="card-title"),
                                html.Hr(),
                                html.P([
                                    html.Strong(f"Taux de participation: "),
                                    f"{pct_participation:.1f}%"
                                ]),
                                html.P([
                                    html.Strong(f"Nombre de feedbacks: "),
                                    f"{avec_feedback:,}"
                                ]),
                                html.P([
                                    html.Strong(f"Sans feedback: "),
                                    f"{sans_feedback:,}"
                                ])
                            ])
                        ])
                    ])
                ])
            ])
            
            return fig_distribution, fig_timeline, fig_demographics, stats

    def render(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Analyse des Sentiments", className="mb-4"),
                    html.Hr(),
                ], md=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Filtres", className="card-title"),
                            html.Hr(),
                            html.Label("Période d'analyse:"),
                            dcc.DateRangePicker(
                                id='date-range',
                                start_date=datetime(2023, 1, 1),
                                end_date=datetime(2024, 12, 31),
                                display_format='DD/MM/YYYY'
                            )
                        ])
                    ], className="mb-4")
                ], md=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(id="feedback-stats")
                ], md=12, className="mb-4")
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="sentiment-distribution")
                ], md=4),
                dbc.Col([
                    dcc.Graph(id="sentiment-timeline")
                ], md=8)
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="sentiment-demographics")
                ], md=12)
            ])
        ], fluid=True)
