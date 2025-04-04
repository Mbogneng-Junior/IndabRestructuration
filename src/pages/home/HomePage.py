import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
import pandas as pd
import folium
from folium import plugins
import numpy as np
from datetime import datetime
from branca.colormap import LinearColormap
from ...services.data.DataService import DataService

class HomePage:
    def __init__(self):
        self.data_service = DataService()

    def init_callbacks(self, app):
        from dash.dependencies import Input, Output, State
        
        def get_coordinates(row):
            """Ajoute les coordonnées pour chaque ville"""
            if 'douala' in str(row['arrondissement_de_residence']).lower():
                base_lat = 4.0500 + np.random.normal(0, 0.01)
                base_lon = 9.7000 + np.random.normal(0, 0.01)
            elif 'yaounde' in str(row['arrondissement_de_residence']).lower():
                base_lat = 3.8667 + np.random.normal(0, 0.01)
                base_lon = 11.5167 + np.random.normal(0, 0.01)
            else:
                base_lat = 4.0500 + np.random.normal(0, 0.01)
                base_lon = 9.7000 + np.random.normal(0, 0.01)
            return pd.Series({'latitude': base_lat, 'longitude': base_lon})
        
        @app.callback(
            [Output("stats-arrondissements", "children"),
             Output("stats-quartiers", "children"),
             Output("stats-donors", "children"),
             Output("stats-successful", "children"),
             Output("stats-ineligible", "children"),
             Output("date-filter", "min_date_allowed"),
             Output("date-filter", "max_date_allowed"),
             Output("date-filter", "start_date"),
             Output("date-filter", "end_date")],
            [Input("location-filter", "value"),
             Input("date-filter", "start_date"),
             Input("date-filter", "end_date")]
        )
        def update_stats(location, start_date, end_date):
            """Met à jour les statistiques"""
            df = self.data_service.get_donor_data()
            df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
            
            # Filtrer par ville et date
            if location and location != 'all':
                df = df[df['arrondissement_de_residence'].str.contains(location, case=False, na=False)]
            
            if start_date and end_date:
                df = df[(df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()) &
                       (df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date())]
            
            # Calculer les statistiques
            total_arrondissements = df['arrondissement_de_residence'].nunique()
            total_quartiers = df['quartier_de_residence'].nunique()
            total_donors = len(df)
            successful_donations = len(df[df['eligibilite_au_don'] == 'eligible'])
            ineligible_donations = len(df[df['eligibilite_au_don'] != 'eligible'])
            
            # Dates pour le filtre
            min_date = df['date_de_remplissage'].min()
            max_date = df['date_de_remplissage'].max()
            
            return (
                str(total_arrondissements),
                str(total_quartiers),
                f"{total_donors:,}",
                f"{successful_donations:,}",
                f"{ineligible_donations:,}",
                min_date.date(),
                max_date.date(),
                min_date.date(),
                max_date.date()
            )
        
        @app.callback(
            [Output("donor-map", "srcDoc"),
             Output("donor-stats-graph", "figure"),
             Output("donor-geo-distribution", "figure")],
            [Input("location-filter", "value"),
             Input("zone-filter", "value"),
             Input("date-filter", "start_date"),
             Input("date-filter", "end_date")]
        )
        def update_visualizations(location, zone_type, start_date, end_date):
            # Charger les données
            df = self.data_service.get_donor_data()
            df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
            
            # Ajouter les coordonnées
            df[['latitude', 'longitude']] = df.apply(get_coordinates, axis=1)
            
            # Filtrer par ville et date
            if location and location != 'all':
                df = df[df['arrondissement_de_residence'].str.contains(location, case=False, na=False)]
            
            if start_date and end_date:
                df = df[
                    (df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()) &
                    (df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date())
                ]
            
            # Créer la carte avec folium
            def create_map(df, zone_type):
                if location == 'douala':
                    center = [4.0500, 9.7000]
                    zoom = 12
                elif location == 'yaounde':
                    center = [3.8667, 11.5167]
                    zoom = 12
                else:
                    center = [4.0500, 9.7000]
                    zoom = 6
                
                m = folium.Map(
                    location=center,
                    zoom_start=zoom,
                    tiles='cartodbpositron'
                )
                
                # Ajouter la couche de chaleur
                heat_data = [[row['latitude'], row['longitude']] for index, row in df.iterrows()]
                plugins.HeatMap(
                    heat_data,
                    radius=15,
                    blur=10,
                    gradient={0.4: '#1a1f3c', 0.65: '#c62828', 1: '#ff5f52'}
                ).add_to(m)
                
                # Créer les clusters de points
                marker_cluster = plugins.MarkerCluster(
                    options={
                        'spiderfyOnMaxZoom': True,
                        'showCoverageOnHover': True,
                        'zoomToBoundsOnClick': True
                    }
                ).add_to(m)
                
                # Ajouter les points individuels
                for idx, row in df.iterrows():
                    color = '#c62828' if row['eligibilite_au_don'].lower() == 'eligible' else '#1a1f3c'
                    
                    folium.CircleMarker(
                        location=[row['latitude'], row['longitude']],
                        radius=3,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7,
                        popup=f"Quartier: {row['quartier_de_residence']}<br>Age: {row['age']}"
                    ).add_to(marker_cluster)
                
                return m._repr_html_()
            
            # Créer les graphiques
            def create_donor_stats(df):
                eligibility_counts = df['eligibilite_au_don'].value_counts()
                fig = px.pie(
                    values=eligibility_counts.values,
                    names=eligibility_counts.index,
                    title="Répartition des donneurs par éligibilité",
                    color_discrete_sequence=['#4CAF50', '#FF9800', '#f44336']
                )
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font={'color': '#1a1f3c'},
                    showlegend=True
                )
                return fig
            
            def create_geo_distribution(df):
                if zone_type == 'quartier':
                    group_by = 'quartier_de_residence'
                else:
                    group_by = 'arrondissement_de_residence'
                
                geo_stats = df.groupby(group_by).size().reset_index(name='count')
                geo_stats = geo_stats.sort_values('count', ascending=True)
                
                fig = px.bar(
                    geo_stats,
                    x='count',
                    y=group_by,
                    orientation='h',
                    title=f"Répartition des donneurs par {group_by.replace('_', ' ').title()}",
                    color='count',
                    color_continuous_scale=['#1a1f3c', '#c62828']
                )
                
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font={'color': '#1a1f3c'},
                    showlegend=False,
                    xaxis_title="Nombre de donneurs",
                    yaxis_title=group_by.replace('_', ' ').title()
                )
                
                return fig
            
            # Retourner les visualisations
            map_html = create_map(df, zone_type)
            donor_stats = create_donor_stats(df)
            geo_distribution = create_geo_distribution(df)
            
            return map_html, donor_stats, geo_distribution

    def render(self):
        """Rendu de la page d'accueil"""
        # Charger les données pour les statistiques initiales
        df = self.data_service.get_donor_data()
        total_donors = len(df)
        total_arrondissements = df['arrondissement_de_residence'].nunique()
        total_quartiers = df['quartier_de_residence'].nunique()
        successful_donations = len(df[df['eligibilite_au_don'] == 'eligible'])
        ineligible_donations = len(df[df['eligibilite_au_don'] != 'eligible'])
        
        return html.Div([
            # En-tête avec titre et bouton
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H1("Campagne de Don de Sang", 
                               className="app-title text-center mb-2"),
                        html.P("Analyse et Optimisation des Campagnes de Don de Sang en Afrique",
                              className="app-subtitle text-center mb-4"),
                        html.Div([
                            dbc.Button(
                                "Explorer le Dashboard",
                                href="/donor-profiles",
                                className="explore-button mx-auto"
                            )
                        ], className="text-center mb-5")
                    ], width=12)
                ])
            ], fluid=True, className="header-container"),
            
            # Section des statistiques principales
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.Div([
                                html.Span(className="stat-icon-bg"),
                                html.I(className="fas fa-building stat-icon")
                            ], className="stat-icon-wrapper"),
                            html.H3(id="stats-arrondissements",
                                   children=f"{total_arrondissements}", 
                                   className="stat-value"),
                            html.P("Arrondissements", className="stat-label"),
                            html.Small("Zones couvertes", className="stat-detail")
                        ], className="stat-card")
                    ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
                    
                    dbc.Col([
                        dbc.Card([
                            html.Div([
                                html.Span(className="stat-icon-bg"),
                                html.I(className="fas fa-home stat-icon")
                            ], className="stat-icon-wrapper"),
                            html.H3(id="stats-quartiers",
                                   children=f"{total_quartiers}", 
                                   className="stat-value"),
                            html.P("Quartiers", className="stat-label"),
                            html.Small("Zones de collecte", className="stat-detail")
                        ], className="stat-card")
                    ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
                    
                    dbc.Col([
                        dbc.Card([
                            html.Div([
                                html.Span(className="stat-icon-bg"),
                                html.I(className="fas fa-users stat-icon")
                            ], className="stat-icon-wrapper"),
                            html.H3(id="stats-donors",
                                   children=f"{total_donors:,}", 
                                   className="stat-value"),
                            html.P("Donneurs", className="stat-label"),
                            html.Small("Total participants", className="stat-detail")
                        ], className="stat-card")
                    ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
                    
                    dbc.Col([
                        dbc.Card([
                            html.Div([
                                html.Span(className="stat-icon-bg success"),
                                html.I(className="fas fa-check-circle stat-icon")
                            ], className="stat-icon-wrapper"),
                            html.H3(id="stats-successful",
                                   children=f"{successful_donations:,}", 
                                   className="stat-value text-success"),
                            html.P("Dons Éligibles", className="stat-label"),
                            html.Small(f"{(successful_donations/total_donors*100):.1f}% du total", className="stat-detail")
                        ], className="stat-card")
                    ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
                    
                    dbc.Col([
                        dbc.Card([
                            html.Div([
                                html.Span(className="stat-icon-bg danger"),
                                html.I(className="fas fa-times-circle stat-icon")
                            ], className="stat-icon-wrapper"),
                            html.H3(id="stats-ineligible",
                                   children=f"{ineligible_donations:,}", 
                                   className="stat-value text-danger"),
                            html.P("Dons Non Éligibles", className="stat-label"),
                            html.Small(f"{(ineligible_donations/total_donors*100):.1f}% du total", className="stat-detail")
                        ], className="stat-card")
                    ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
                ], className="mb-4"),
                
                # Section de la carte et des filtres
                dbc.Row([
                    # Filtres
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Filtres", className="filter-title mb-4"),
                                html.Div([
                                    html.Label("Localisation", className="filter-label"),
                                    dcc.Dropdown(
                                        id='location-filter',
                                        options=[
                                            {'label': 'Tout le Cameroun', 'value': 'all'},
                                            {'label': 'Douala', 'value': 'douala'},
                                            {'label': 'Yaoundé', 'value': 'yaounde'}
                                        ],
                                        value='all',
                                        className="filter-dropdown"
                                    ),
                                ], className="filter-group"),
                                
                                html.Div([
                                    html.Label("Zone", className="filter-label"),
                                    dcc.Dropdown(
                                        id='zone-filter',
                                        options=[
                                            {'label': 'Tous les quartiers', 'value': 'tous'},
                                            {'label': 'Par Quartier', 'value': 'quartier'},
                                            {'label': 'Par Arrondissement', 'value': 'arrondissement'}
                                        ],
                                        value='tous',
                                        className="filter-dropdown"
                                    ),
                                ], className="filter-group"),
                                
                                html.Div([
                                    html.Label("Période", className="filter-label"),
                                    dcc.DatePickerRange(
                                        id='date-filter',
                                        className="filter-date"
                                    ),
                                ], className="filter-group"),
                            ])
                        ], className="filter-card")
                    ], width=12, lg=3),
                    
                    # Carte
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Iframe(
                                    id='donor-map',
                                    style={
                                        'width': '100%',
                                        'height': '400px',
                                        'border': 'none',
                                        'borderRadius': '8px'
                                    }
                                )
                            ])
                        ], className="map-card")
                    ], width=12, lg=9),
                ], className="mb-4"),
                
                # Graphiques
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(
                                    id='donor-stats-graph',
                                    config={'displayModeBar': False}
                                )
                            ])
                        ], className="chart-container")
                    ], width=12, lg=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(
                                    id='donor-geo-distribution',
                                    config={'displayModeBar': False}
                                )
                            ])
                        ], className="chart-container")
                    ], width=12, lg=6),
                ])
            ], fluid=True)
        ])
