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
import plotly.graph_objects as go

VILLES_COORD = {
    'douala': {'lat': 4.0500, 'lon': 9.7000, 'zoom': 12},
    'yaounde': {'lat': 3.8667, 'lon': 11.5167, 'zoom': 12},
    'bafoussam': {'lat': 5.4667, 'lon': 10.4167, 'zoom': 12},
    'edea': {'lat': 3.7979, 'lon': 10.13, 'zoom': 12},
    'meiganga': {'lat': 61.5178, 'lon': 14.2892, 'zoom': 12},
    'dibamba': {'lat': 4.0196, 'lon': 9.8543, 'zoom': 12},
    'buea': {'lat': 4.1528, 'lon': 9.2531, 'zoom': 12},
    'kribi': {'lat': 2.9404, 'lon': 9.9098, 'zoom': 12},
    'njombe-penja': {'lat': 4.6377, 'lon': 9.6868, 'zoom': 12},
    'tiko': {'lat': 4.0836, 'lon': 9.3548, 'zoom': 12},
    'manjo': {'lat': 4.8476, 'lon': 9.8179, 'zoom': 12},
    'lolodorf': {'lat': 3.2335, 'lon': 10.7292, 'zoom': 12},
    'batie': {'lat': 5.2925, 'lon': 10.2653, 'zoom': 12},
    'dibombari': {'lat': 4.1775, 'lon': 9.6545, 'zoom': 12},
    'tombel': {'lat': 4.7452, 'lon': 9.6707, 'zoom': 12},
    'limbe': {'lat': 4.0227, 'lon': 9.1962, 'zoom': 12}
}

ARR_COORD = {
    'douala 3': {'lat': 4.0372, 'lon': 9.75652, 'zoom': 30}, 
    'douala 5': {'lat': 4.0898, 'lon': 9.7406, 'zoom': 30},
    'douala 2': {'lat': 4.0657, 'lon': 9.7145, 'zoom': 30},
    'douala 1': {'lat': 4.0665, 'lon': 9.7176, 'zoom': 30},
    'yaounde 1': {'lat': 3.9082, 'lon': 11.5312, 'zoom': 30},
    'douala 4': {'lat': 4.0702, 'lon': 9.6854, 'zoom': 30},
    'dschang': {'lat': 5.4458, 'lon': 10.0481, 'zoom': 30},
    'yaounde 5': {'lat': 3.8947, 'lon': 11.5506, 'zoom': 30},
    'yaounde 4': {'lat': 3.8555, 'lon': 11.5375, 'zoom': 30},
    'dibamba': {'lat': 4.0196, 'lon': 9.8543, 'zoom': 30},
    'buea': {'lat': 4.1528, 'lon': 9.2531, 'zoom': 30},
    'njombe-penja': {'lat': 4.6377, 'lon': 9.6868, 'zoom': 30},
    'tiko': {'lat': 4.0836, 'lon': 9.3548, 'zoom': 30},
    'edea 2': {'lat': 3.8522, 'lon': 10.0866, 'zoom': 30},
    'manjo': {'lat': 4.8476, 'lon': 9.8179, 'zoom': 30},
    'nkolafamba': {'lat': 3.8571, 'lon': 11.6643, 'zoom': 30},
    'lolodorf': {'lat': 3.2335, 'lon': 10.7292, 'zoom': 30},
    'yaounde 2': {'lat': 3.8916, 'lon': 11.5375, 'zoom': 30},
    'douala 6': {'lat': 4.0384, 'lon': 9.7113, 'zoom': 30},
    'batie': {'lat': 5.2925, 'lon': 10.2653, 'zoom': 30},
    'bomono ba mbegue': {'lat': 4.1367, 'lon': 9.5859, 'zoom': 30},
    'dibombari': {'lat': 4.1775, 'lon': 9.6545, 'zoom': 30},
    'yaounde 6': {'lat': 3.8398, 'lon': 11.4908, 'zoom': 30},
    'meiganga': {'lat': 61.5178, 'lon': 14.2892, 'zoom': 30},
    'tombel': {'lat': 4.7452, 'lon': 9.6707, 'zoom': 30},
    'limbe': {'lat': 4.0227, 'lon': 9.1962, 'zoom': 30}
}

class MappingPage:
    total_arrondissements = 0
    total_quartiers = 0
    
    def __init__(self):
        self.data_service = DataService()
        self.cities = VILLES_COORD

    def init_callbacks(self, app):
        from dash.dependencies import Input, Output, State

        def get_coordinates(row):
            """Ajoute les coordonnées pour chaque point en fonction de l'arrondissement"""
            arr = str(row['arrondissement_de_residence']).lower()
            
            # Chercher d'abord dans les coordonnées d'arrondissement
            for arr_name, coords in ARR_COORD.items():
                if arr_name.lower() in arr:
                    return pd.Series({
                        'latitude': coords['lat'] + np.random.normal(0, 0.001),
                        'longitude': coords['lon'] + np.random.normal(0, 0.001)
                    })
            
            # Si pas trouvé, chercher dans les coordonnées de ville
            for city_name, coords in self.cities.items():
                if city_name.lower() in arr:
                    return pd.Series({
                        'latitude': coords['lat'] + np.random.normal(0, 0.005),
                        'longitude': coords['lon'] + np.random.normal(0, 0.005)
                    })
            
            # Si toujours pas trouvé, utiliser les coordonnées par défaut de Douala
            return pd.Series({
                'latitude': self.cities['douala']['lat'] + np.random.normal(0, 0.01),
                'longitude': self.cities['douala']['lon'] + np.random.normal(0, 0.01)
            })

        @app.callback(
            Output("arrondissement-select", "options"),
            [Input("city-select", "value")]
        )
        def update_arrondissements(city):
            if not city:
                # Si aucune ville n'est sélectionnée, montrer tous les arrondissements
                return [{'label': arr, 'value': arr} for arr in ARR_COORD.keys()]
            
            # Filtrer les arrondissements pour la ville sélectionnée
            arr_options = [
                {'label': arr_name, 'value': arr_name}
                for arr_name in ARR_COORD.keys()
                if city.lower() in arr_name.lower()
            ]
            return sorted(arr_options, key=lambda x: x['label'])

        @app.callback(
            Output("quartier-select", "options"),
            [Input("arrondissement-select", "value")]
        )
        def update_quartiers(arrondissement):
            df = self.data_service.get_donor_data()
            if not arrondissement:
                # Si aucun arrondissement n'est sélectionné, montrer tous les quartiers
                quartiers = df['quartier_de_residence'].unique()
            else:
                # Filtrer les quartiers pour l'arrondissement sélectionné
                quartiers = df[df['arrondissement_de_residence'] == arrondissement]['quartier_de_residence'].unique()
            
            # Filtrer les valeurs non valides et trier
            quartiers = [q for q in quartiers if q and str(q).lower() not in ['nan', 'none', 'pas précisé']]
            return [{'label': q, 'value': q} for q in sorted(quartiers)]

        @app.callback(
            [Output("stats-arrondissements", "children"),
             Output("stats-quartiers", "children"),
             Output("map-container", "srcDoc"),
             Output("district-chart", "figure"),
             Output("quartier-chart", "figure"),
             Output("city-chart", "figure"),
             Output("proportions-stats", "children")],
            [Input("city-select", "value"),
             Input("arrondissement-select", "value"),
             Input("date-range", "start_date"),
             Input("date-range", "end_date")]
        )
        def update_visualizations(city, arrondissement, start_date, end_date):
            # Charger les données
            df = self.data_service.get_donor_data()

            # Calculer les statistiques
            total_arrondissements = df['arrondissement_de_residence'].nunique()
            total_quartiers = df['quartier_de_residence'].nunique()
            df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
            
            # Ajouter les coordonnées
            df[['latitude', 'longitude']] = df.apply(get_coordinates, axis=1)
            
            # Filtrer par date
            if start_date and end_date:
                mask = (df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()) & \
                      (df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date())
                df = df[mask]

            # Déterminer le centre et le zoom de la carte
            if arrondissement:
                arr_lower = arrondissement.lower()
                for arr_name, coords in ARR_COORD.items():
                    if arr_name.lower() == arr_lower:
                        center = [coords['lat'], coords['lon']]
                        zoom = coords['zoom']
                        break
                else:
                    if city and city.lower() in self.cities:
                        center = [self.cities[city.lower()]['lat'], self.cities[city.lower()]['lon']]
                        zoom = self.cities[city.lower()]['zoom']
                    else:
                        center = [4.0500, 9.7000]  # Centre du Cameroun
                        zoom = 6
            elif city and city.lower() in self.cities:
                center = [self.cities[city.lower()]['lat'], self.cities[city.lower()]['lon']]
                zoom = self.cities[city.lower()]['zoom']
            else:
                # Vue par défaut centrée sur le Cameroun pour voir toutes les villes
                center = [4.0500, 9.7000]  # Centre du Cameroun
                zoom = 6

            # Créer la carte
            m = folium.Map(
                location=center,
                zoom_start=zoom,
                tiles='cartodbpositron'
            )

            # Filtrer les données
            if arrondissement:
                df_filtered = df[df['arrondissement_de_residence'] == arrondissement]
            elif city:
                df_filtered = df[df['arrondissement_de_residence'].str.contains(city, case=False, na=False)]
            else:
                df_filtered = df

            # Créer les clusters de points
            marker_cluster = plugins.MarkerCluster(
                options={
                    'spiderfyOnMaxZoom': True,
                    'showCoverageOnHover': True,
                    'zoomToBoundsOnClick': True
                }
            ).add_to(m)

            # Ajouter les points individuels
            for idx, row in df_filtered.iterrows():
                color = '#c62828' if row['eligibilite_au_don'].lower() == 'eligible' else '#1a1f3c'
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=3,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    popup=f"Quartier: {row['quartier_de_residence']}<br>Arrondissement: {row['arrondissement_de_residence']}<br>Age: {row['age']}"
                ).add_to(marker_cluster)

            # Ajouter des marqueurs pour toutes les villes
            for city_name, coords in self.cities.items():
                folium.CircleMarker(
                    location=[coords['lat'], coords['lon']],
                    radius=8,
                    color='#ff0000',
                    fill=True,
                    fillColor='#',
                    fillOpacity=0.7,
                    popup=city_name.title(),
                    weight=2
                ).add_to(m)

            # Créer les graphiques avec les données filtrées
            district_df = df[~df['arrondissement_de_residence'].isin(['pas précisé', np.nan])]['arrondissement_de_residence'].value_counts().reset_index()
            district_df.columns = ['arrondissement', 'nombre']
            
            quartier_df = df[~df['quartier_de_residence'].isin(['pas précisé', np.nan])]['quartier_de_residence'].value_counts().reset_index()
            quartier_df.columns = ['quartier', 'nombre']
            
            city_df = df[~df['ville'].isin(['inconnu', np.nan])]['ville'].value_counts().reset_index()
            city_df.columns = ['ville', 'nombre']

            # Créer les graphiques avec les données filtrées
            district_fig = px.bar(
                district_df,
                x='arrondissement',
                y='nombre',
                color='nombre',
                color_continuous_scale=['#1a1f3c', '#c62828']
            )
            district_fig.update_layout(
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#1a1f3c'},
                showlegend=False
            )

            quartier_fig = px.bar(
                quartier_df,
                x='quartier',
                y='nombre',
                color='nombre',
                color_continuous_scale=['#1a1f3c', '#c62828']
            )
            quartier_fig.update_layout(
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#1a1f3c'},
                showlegend=False
            )

            city_fig = px.bar(
                city_df,
                x='ville',
                y='nombre',
                color='nombre',
                color_continuous_scale=['#1a1f3c', '#c62828']
            )
            city_fig.update_layout(
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#1a1f3c'},
                showlegend=False
            )

            # Créer les diagrammes circulaires pour les proportions
            ville_precisee = len(df) - (df['ville'].isna().sum() + df[df['ville'] == 'inconnu'].shape[0])
            ville_non_precisee = df['ville'].isna().sum() + df[df['ville'] == 'inconnu'].shape[0]
            
            arr_precise = len(df) - (df['arrondissement_de_residence'].isna().sum() + df[df['arrondissement_de_residence'] == 'pas précisé'].shape[0])
            arr_non_precise = df['arrondissement_de_residence'].isna().sum() + df[df['arrondissement_de_residence'] == 'pas précisé'].shape[0]
            
            quartier_precise = len(df) - (df['quartier_de_residence'].isna().sum() + df[df['quartier_de_residence'] == 'pas précisé'].shape[0])
            quartier_non_precise = df['quartier_de_residence'].isna().sum() + df[df['quartier_de_residence'] == 'pas précisé'].shape[0]
            
            fig_ville = go.Figure(data=[go.Pie(
                labels=['Précisé', 'Non précisé'],
                values=[ville_precisee, ville_non_precisee],
                hole=.3,
                marker_colors=['#1a1f3c', '#c62828']
            )])
            fig_ville.update_layout(
                title="Proportion des villes non précisées",
                height=300,
                showlegend=True
            )
            
            fig_arr = go.Figure(data=[go.Pie(
                labels=['Précisé', 'Non précisé'],
                values=[arr_precise, arr_non_precise],
                hole=.3,
                marker_colors=['#1a1f3c', '#c62828']
            )])
            fig_arr.update_layout(
                title="Proportion des arrondissements non précisés",
                height=300,
                showlegend=True
            )
            
            fig_quartier = go.Figure(data=[go.Pie(
                labels=['Précisé', 'Non précisé'],
                values=[quartier_precise, quartier_non_precise],
                hole=.3,
                marker_colors=['#1a1f3c', '#c62828']
            )])
            fig_quartier.update_layout(
                title="Proportion des quartiers non précisés",
                height=300,
                showlegend=True
            )
            
            proportions_stats = html.Div([
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(figure=fig_ville)
                    ], md=4),
                    dbc.Col([
                        dcc.Graph(figure=fig_arr)
                    ], md=4),
                    dbc.Col([
                        dcc.Graph(figure=fig_quartier)
                    ], md=4)
                ])
            ])

            # Sauvegarder la carte en HTML
            map_html = m._repr_html_()
            
            return (
                f"{total_arrondissements:,}",
                f"{total_quartiers:,}",
                map_html,
                district_fig,
                quartier_fig,
                city_fig,
                proportions_stats
            )

    def render(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Cartographie de la Répartition", className="mb-4 text-black"),
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Filtres", className="card-title"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Ville"),
                                    dcc.Dropdown(
                                        id="city-select",
                                        options=[{'label': city.title(), 'value': city} for city in VILLES_COORD.keys()],
                                        placeholder="Sélectionnez une ville"
                                    )
                                ], md=4),
                                dbc.Col([
                                    html.Label("Arrondissement"),
                                    dcc.Dropdown(
                                        id="arrondissement-select",
                                        placeholder="Sélectionnez un arrondissement"
                                    )
                                ], md=4),
                                dbc.Col([
                                    html.Label("Période"),
                                    dcc.DatePickerRange(
                                        id="date-range",
                                        display_format="DD/MM/YYYY"
                                    )
                                ], md=4),
                            ], className="mb-3"),
                        ])
                    ], className="mb-4")
                ])
            ]),

            dbc.Row([
                dbc.Col([
                    html.Iframe(id="map-container", width="100%", height="600px")
                ], md=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.Div([
                            html.Span(className="stat-icon-bg"),
                            html.I(className="fas fa-building stat-icon")
                        ], className="stat-icon-wrapper"),
                        html.H3(id="stats-arrondissements",
                               children=f"{self.total_arrondissements}", 
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
                               children=f"{self.total_quartiers}", 
                               className="stat-value"),
                        html.P("Quartiers", className="stat-label"),
                        html.Small("Zones de collecte", className="stat-detail")
                    ], className="stat-card")
                ], xs=12, sm=6, md=4, lg=3, className="mb-3"),
            ]),

            html.Div(id="proportions-stats"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Répartition des donneurs par ville"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='city-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card mb-4")
                ], md=12),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Répartition des donneurs par arrondissement"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='district-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card mb-4")
                ], md=12),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Répartition des donneurs par quartier"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='quartier-chart',
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card")
                ], md=12)
            ]),
        ], fluid=True)
