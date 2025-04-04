import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from ...services.data.DataService import DataService

class CampaignAnalysisPage:
    def __init__(self):
        self.data_service = DataService()

    def init_callbacks(self, app):
        @app.callback(
            Output('district-filter', 'options'),
            [Input('city-filter', 'value')]
        )
        def update_district_options(city):
            df = self.data_service.get_donor_data()
            if city != 'all':
                df = df[df['ville'].str.contains(city, case=False, na=False)]
            districts = df['arrondissement_de_residence'].unique()
            return [{'label': d, 'value': d} for d in sorted(districts)]
        
        @app.callback(
            Output('neighborhood-filter', 'options'),
            [Input('city-filter', 'value'),
             Input('district-filter', 'value')]
        )
        def update_neighborhood_options(city, district):
            df = self.data_service.get_donor_data()
            if city != 'all':
                df = df[df['ville'].str.contains(city, case=False, na=False)]
            if district:
                df = df[df['arrondissement_de_residence'] == district]
            neighborhoods = df['quartier_de_residence'].unique()
            return [{'label': n, 'value': n} for n in sorted(neighborhoods)]
        
        @app.callback(
            [Output('total-donations', 'children'),
             Output('eligibility-rate', 'children'),
             Output('total-neighborhoods', 'children'),
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
                df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
                
                # Appliquer les filtres
                if city != 'all':
                    df = df[df['ville'].str.contains(city, case=False, na=False)]
                if district:
                    df = df[df['arrondissement_de_residence'] == district]
                if neighborhood:
                    df = df[df['quartier_de_residence'] == neighborhood]
                if start_date:
                    df = df[df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()]
                if end_date:
                    df = df[df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date()]
                
                # Calculer les statistiques
                total_donations = len(df)
                eligibility_rate = (df['eligibilite_au_don'] == 'eligible').mean()
                total_neighborhoods = df['quartier_de_residence'].nunique()
                
                # 1. Graphique temporel avec meilleure échelle
                timeline_df = df.groupby('date_de_remplissage').size().reset_index(name='Nombre de dons')
                timeline_fig = px.line(
                    timeline_df,
                    x='date_de_remplissage',
                    y='Nombre de dons',
                    title="Nombre de dons en fonction de la date de remplissage"
                )
                
                # Améliorer l'échelle et le style
                timeline_fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Nombre de dons",
                    template='plotly_white',
                    yaxis=dict(
                        rangemode='tozero',
                        tickformat=',d'
                    ),
                    margin=dict(l=50, r=20, t=40, b=30)
                )
                
                # 2. Distribution de l'éligibilité par âge
                eligible_df = df[df['eligibilite_au_don'] == 'eligible'].copy()
                
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
                    title="Distribution des donneurs éligibles par âge",
                    labels={'age_group': 'Groupe d\'âge'}
                )
                
                age_dist_fig.update_layout(
                    template='plotly_white',
                    xaxis_tickangle=-45,
                    bargap=0.1,
                    margin=dict(l=50, r=20, t=40, b=100),
                    yaxis=dict(
                        rangemode='tozero',
                        tickformat=',d'
                    )
                )
                
                return (
                    f"{total_donations:,}",
                    f"{eligibility_rate:.1%}",
                    f"{total_neighborhoods:,}",
                    timeline_fig,
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
                return "0", "0%", "0", empty_fig, empty_fig

        @app.callback(
            [Output('campaign-total-donations', 'children'),
             Output('campaign-peak-period', 'children'),
             Output('campaign-growth-rate', 'children')],
            [Input('campaign-date-range', 'start_date'),
             Input('campaign-date-range', 'end_date')]
        )
        def update_campaign_kpis(start_date, end_date):
            df = self.data_service.get_donor_data()
            df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
            
            if df.empty:
                return "0", "N/A", "0%"
            
            # Conversion des dates
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            
            # Filtrage par date
            mask = (df['date_de_remplissage'] >= start_date) & (df['date_de_remplissage'] <= end_date)
            filtered_df = df[mask]
            
            # Total des dons
            total_dons = len(filtered_df)
            
            # Période la plus active (mois)
            if not filtered_df.empty:
                monthly_counts = filtered_df['date_de_remplissage'].dt.to_period('M').value_counts()
                peak_month = monthly_counts.index[0] if not monthly_counts.empty else "N/A"
                peak_month = str(peak_month)
            else:
                peak_month = "N/A"
                
            # Taux de croissance
            if not filtered_df.empty:
                monthly_data = filtered_df.groupby(filtered_df['date_de_remplissage'].dt.to_period('M')).size()
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

    def render(self):
        """Rendu de la page d'analyse des campagnes"""
        return html.Div([
            # En-tête
            html.Div([
                html.H2("Analyse des Campagnes", className="mb-4"),
                html.P("Suivez et analysez les performances de vos campagnes de don de sang", className="text-muted")
            ], className="header-section mb-4"),
            
            # Filtres
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Ville"),
                                dcc.Dropdown(
                                    id='city-filter',
                                    options=[
                                        {'label': 'Toutes', 'value': 'all'},
                                        {'label': 'Douala', 'value': 'douala'},
                                        {'label': 'Yaoundé', 'value': 'yaounde'}
                                    ],
                                    value='all',
                                    className="mb-2"
                                )
                            ], md=3),
                            dbc.Col([
                                html.Label("Arrondissement"),
                                dcc.Dropdown(
                                    id='district-filter',
                                    placeholder="Sélectionner un arrondissement",
                                    className="mb-2"
                                )
                            ], md=3),
                            dbc.Col([
                                html.Label("Quartier"),
                                dcc.Dropdown(
                                    id='neighborhood-filter',
                                    placeholder="Sélectionner un quartier",
                                    className="mb-2"
                                )
                            ], md=3),
                            dbc.Col([
                                html.Label("Période"),
                                dcc.DatePickerRange(
                                    id='date-range',
                                    className="mb-2"
                                )
                            ], md=3)
                        ])
                    ])
                ], className="filter-card mb-4")
            ], className="filter-section"),
            
            # Statistiques générales
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Nombre total de dons", className="card-title"),
                            html.H2(id="total-donations", className="text-primary")
                        ])
                    ], className="stat-card")
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Taux d'éligibilité", className="card-title"),
                            html.H2(id="eligibility-rate", className="text-success")
                        ])
                    ], className="stat-card")
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Nombre de quartiers", className="card-title"),
                            html.H2(id="total-neighborhoods", className="text-info")
                        ])
                    ], className="stat-card")
                ], md=4)
            ], className="mb-4"),
            
            # Graphiques
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Évolution des dons"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='donations-timeline',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card mb-4")
                ], md=12),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribution par âge des donneurs éligibles"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='eligibility-age-distribution',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card")
                ], md=12)
            ])
        ], className="campaign-container")
