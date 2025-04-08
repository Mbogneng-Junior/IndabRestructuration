import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from ...services.data.DataService import DataService
import os

class CampaignAnalysisPage:
    def __init__(self):
        self.data_service = DataService()

    def init_callbacks(self, app):
        @app.callback(
            Output('district-filter', 'options'),
            [Input('city-filter', 'value')]
        )
        def update_district_options(city):
            try:
                df = self.data_service.get_donor_data()
                
                # Vérifier si les colonnes existent
                if 'ville' not in df.columns:
                    print("Colonne 'ville' non trouvée. Colonnes disponibles:", df.columns)
                    return []
                
                if city and city != 'all':
                    df = df[df['ville'].str.contains(city, case=False, na=False)]
                
                # Utiliser une valeur par défaut si la colonne n'existe pas
                district_column = 'arrondissement' if 'arrondissement' in df.columns else 'arrondissement_de_residence'
                if district_column not in df.columns:
                    print(f"Colonne {district_column} non trouvée. Colonnes disponibles:", df.columns)
                    return []
                
                districts = df[district_column].dropna().unique()
                return [{'label': str(d), 'value': str(d)} for d in sorted(districts)]
            except Exception as e:
                print(f"Erreur dans update_district_options: {str(e)}")
                return []

        @app.callback(
            Output('neighborhood-filter', 'options'),
            [Input('city-filter', 'value'),
             Input('district-filter', 'value')]
        )
        def update_neighborhood_options(city, district):
            try:
                df = self.data_service.get_donor_data()
                
                if city and city != 'all':
                    df = df[df['ville'].str.contains(city, case=False, na=False)]
                
                district_column = 'arrondissement' if 'arrondissement' in df.columns else 'arrondissement_de_residence'
                if district and district_column in df.columns:
                    df = df[df[district_column] == district]
                
                neighborhood_column = 'quartier' if 'quartier' in df.columns else 'quartier_de_residence'
                if neighborhood_column not in df.columns:
                    print(f"Colonne {neighborhood_column} non trouvée. Colonnes disponibles:", df.columns)
                    return []
                
                neighborhoods = df[neighborhood_column].dropna().unique()
                return [{'label': str(n), 'value': str(n)} for n in sorted(neighborhoods)]
            except Exception as e:
                print(f"Erreur dans update_neighborhood_options: {str(e)}")
                return []

        @app.callback(
            [Output('total-donations', 'children'),
             Output('eligibility-rate', 'children'),
             Output('total-neighborhoods', 'children'),
             Output('peak-year', 'children'),
             Output('donations-timeline', 'figure'),
             Output('eligibility-age-distribution', 'figure')],
            [Input('city-filter', 'value'),
             Input('district-filter', 'value'),
             Input('neighborhood-filter', 'value'),
             Input('date-range', 'start_date'),
             Input('date-range', 'end_date')]
        )
        def update_campaign_analysis(city, district, neighborhood, start_date, end_date):
            try:
                df = self.data_service.get_donor_data()
                
                # Charger le dataset des dons effectifs
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                donations_file = os.path.join(current_dir, 'data', 'data_cleaned.csv')
                donations_df = pd.read_csv(donations_file)
                donations_df['date'] = pd.to_datetime(donations_df['date'])
                
                # Traitement du premier dataset (données de base)
                date_column = 'date_de_remplissage'
                if date_column not in df.columns:
                    print(f"Colonne {date_column} non trouvée. Colonnes disponibles:", df.columns)
                    raise ValueError(f"Colonne {date_column} non trouvée")
                
                df[date_column] = pd.to_datetime(df[date_column])
                
                # Appliquer les filtres avec vérification des colonnes
                if city and city != 'all' and 'ville' in df.columns:
                    df = df[df['ville'].str.contains(city, case=False, na=False)]
                
                district_column = 'arrondissement' if 'arrondissement' in df.columns else 'arrondissement_de_residence'
                if district and district_column in df.columns:
                    df = df[df[district_column] == district]
                
                neighborhood_column = 'quartier' if 'quartier' in df.columns else 'quartier_de_residence'
                if neighborhood and neighborhood_column in df.columns:
                    df = df[df[neighborhood_column] == neighborhood]
                
                if start_date:
                    df = df[df[date_column].dt.date >= pd.to_datetime(start_date).date()]
                    donations_df = donations_df[donations_df['date'].dt.date >= pd.to_datetime(start_date).date()]
                if end_date:
                    df = df[df[date_column].dt.date <= pd.to_datetime(end_date).date()]
                    donations_df = donations_df[donations_df['date'].dt.date <= pd.to_datetime(end_date).date()]
                
                # Calculer les statistiques
                total_donations = len(df)
                eligibility_column = 'eligibilite_au_don'
                if eligibility_column in df.columns:
                    eligibility_rate = (df[eligibility_column].str.lower() == 'eligible').mean()
                else:
                    eligibility_rate = 0
                
                total_neighborhoods = df[neighborhood_column].nunique() if neighborhood_column in df.columns else 0
                
                # Trouver l'année avec le plus de dons
                yearly_donations = df.groupby(df[date_column].dt.year).size()
                peak_year = yearly_donations.idxmax() if not yearly_donations.empty else "N/A"
                peak_year_count = yearly_donations.max() if not yearly_donations.empty else 0
                
                # Créer le graphique avec les deux courbes
                timeline_df = df.groupby(date_column).size().reset_index(name='Inscriptions')
                donations_timeline = donations_df.groupby('date').size().reset_index(name='Dons effectifs')
                
                fig = go.Figure()
                
                # Ajouter la courbe des inscriptions
                fig.add_trace(go.Scatter(
                    x=timeline_df[date_column],
                    y=timeline_df['Inscriptions'],
                    name='Inscriptions',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                # Ajouter la courbe des dons effectifs
                fig.add_trace(go.Scatter(
                    x=donations_timeline['date'],
                    y=donations_timeline['Dons effectifs'],
                    name='Dons effectifs',
                    line=dict(color='#2ca02c', width=2)
                ))
                
                # Mise à jour du layout
                fig.update_layout(
                    title="Évolution des inscriptions et des dons dans le temps",
                    xaxis_title="Date",
                    yaxis_title="Nombre",
                    template='plotly_white',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    margin=dict(l=50, r=20, t=60, b=30)
                )
                
                # Distribution par âge
                age_dist_fig = go.Figure()
                if 'age' in df.columns and eligibility_column in df.columns:
                    eligible_df = df[df[eligibility_column].str.lower() == 'eligible'].copy()
                    age_bins = list(range(0, 101, 5))
                    age_labels = [f"{i}-{i+4}" for i in range(0, 96, 5)]
                    
                    eligible_df['age_group'] = pd.cut(
                        eligible_df['age'],
                        bins=age_bins,
                        labels=age_labels,
                        include_lowest=True
                    )
                    
                    age_dist = eligible_df.groupby('age_group').size().reset_index(name='Nombre de donneurs éligibles')
                    age_dist_fig = px.bar(
                        age_dist,
                        x='age_group',
                        y='Nombre de donneurs éligibles',
                        title="Distribution des donneurs éligibles par âge"
                    )
                    age_dist_fig.update_layout(
                        xaxis_title="Groupe d'âge",
                        yaxis_title="Nombre de donneurs",
                        template='plotly_white',
                        xaxis_tickangle=-45,
                        bargap=0.1,
                        margin=dict(l=50, r=20, t=40, b=100)
                    )
                
                return (
                    f"{total_donations:,}",
                    f"{eligibility_rate:.1%}",
                    f"{total_neighborhoods:,}",
                    f"Pic en {peak_year} ({peak_year_count:,} dons)",
                    fig,
                    age_dist_fig
                )
                
            except Exception as e:
                print(f"Erreur dans update_campaign_analysis: {str(e)}")
                empty_fig = go.Figure()
                empty_fig.add_annotation(
                    text="Erreur lors du chargement des données",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
                return "0", "0%", "0", "N/A", empty_fig, empty_fig

        @app.callback(
            [Output('campaign-total-donations', 'children'),
             Output('campaign-peak-period', 'children'),
             Output('campaign-growth-rate', 'children')],
            [Input('campaign-date-range', 'start_date'),
             Input('campaign-date-range', 'end_date')]
        )
        def update_campaign_kpis(start_date, end_date):
            try:
                df = self.data_service.get_donor_data()
                date_column = 'date_de_remplissage'
                
                if date_column not in df.columns:
                    return "0", "N/A", "0%"
                
                df[date_column] = pd.to_datetime(df[date_column])
                
                if df.empty:
                    return "0", "N/A", "0%"
                
                # Conversion des dates
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
                
                # Filtrage par date
                mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
                filtered_df = df[mask]
                
                # Total des dons
                total_dons = len(filtered_df)
                
                # Période la plus active (mois)
                if not filtered_df.empty:
                    monthly_counts = filtered_df[date_column].dt.to_period('M').value_counts()
                    peak_month = monthly_counts.index[0] if not monthly_counts.empty else "N/A"
                    peak_month = str(peak_month)
                else:
                    peak_month = "N/A"
                    
                # Taux de croissance
                if not filtered_df.empty:
                    monthly_data = filtered_df.groupby(filtered_df[date_column].dt.to_period('M')).size()
                    if len(monthly_data) > 1:
                        first_month = monthly_data.iloc[0]
                        last_month = monthly_data.iloc[-1]
                        growth = ((last_month - first_month) / first_month) * 100
                        growth_rate = f"{growth:+.1f}%"
                    else:
                        growth_rate = "N/A"
                else:
                    growth_rate = "N/A"
                
                return f"{total_dons:,}", peak_month, growth_rate
                
            except Exception as e:
                print(f"Erreur dans update_campaign_kpis: {str(e)}")
                return "0", "N/A", "0%"

    def render(self):
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H2("Analyse des Campagnes de Don", className="text-primary mb-4")
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Filtres", className="card-title"),
                            html.Div([
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
                                ),
                                dbc.Label("Arrondissement"),
                                dcc.Dropdown(
                                    id='district-filter',
                                    options=[],
                                    className="mb-3"
                                ),
                                dbc.Label("Quartier"),
                                dcc.Dropdown(
                                    id='neighborhood-filter',
                                    options=[],
                                    className="mb-3"
                                ),
                                dbc.Label("Période"),
                                dcc.DatePickerRange(
                                    id='date-range',
                                    className="mb-3"
                                )
                            ])
                        ])
                    ], className="mb-4")
                ], md=3),
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Total des inscriptions", className="card-title"),
                                    html.H3(id="total-donations", className="text-primary")
                                ])
                            ])
                        ], width=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Taux d'éligibilité", className="card-title"),
                                    html.H3(id="eligibility-rate", className="text-success")
                                ])
                            ])
                        ], width=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Quartiers couverts", className="card-title"),
                                    html.H3(id="total-neighborhoods", className="text-info")
                                ])
                            ])
                        ], width=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Année pic", className="card-title"),
                                    html.H3(id="peak-year", className="text-warning")
                                ])
                            ])
                        ], width=3)
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(id="donations-timeline")
                                ])
                            ])
                        ])
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Graph(id="eligibility-age-distribution")
                                ])
                            ])
                        ])
                    ])
                ], md=9)
            ])
        ])
