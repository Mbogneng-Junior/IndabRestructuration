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

class MappingPage:
    def __init__(self):
        self.data_service = DataService()
        self.cities = {
            'douala': {'lat': 4.0500, 'lon': 9.7000, 'zoom': 12},
            'yaounde': {'lat': 3.8667, 'lon': 11.5167, 'zoom': 12},
            'bafoussam': {'lat': 5.4667, 'lon': 10.4167, 'zoom': 12}
        }

    def init_callbacks(self, app):
        from dash.dependencies import Input, Output, State

        @app.callback(
            Output("arrondissement-select", "options"),
            [Input("city-select", "value")]
        )
        def update_arrondissements(city):
            if not city:
                return []
            
            df = self.data_service.get_donor_data()
            arrondissements = df[df['arrondissement_de_residence'].str.contains(city, case=False, na=False)]['arrondissement_de_residence'].unique()
            return [{'label': arr, 'value': arr} for arr in sorted(arrondissements)]

        @app.callback(
            Output("quartier-select", "options"),
            [Input("arrondissement-select", "value")]
        )
        def update_quartiers(arrondissement):
            if not arrondissement:
                return []
            
            df = self.data_service.get_donor_data()
            quartiers = df[df['arrondissement_de_residence'] == arrondissement]['quartier_de_residence'].unique()
            return [{'label': q, 'value': q} for q in sorted(quartiers)]

        @app.callback(
            [Output("map-container", "srcDoc"),
             Output("district-chart", "figure"),
             Output("quartier-chart", "figure")],
            [Input("city-select", "value"),
             Input("arrondissement-select", "value"),
             Input("quartier-select", "value"),
             Input("date-range", "start_date"),
             Input("date-range", "end_date")]
        )
        def update_visualizations(city, arrondissement, quartier, start_date, end_date):
            df = self.data_service.get_donor_data()
            df['date_de_remplissage'] = pd.to_datetime(df['date_de_remplissage'])
            
            # Filtrer par date
            if start_date and end_date:
                mask = (df['date_de_remplissage'].dt.date >= pd.to_datetime(start_date).date()) & \
                      (df['date_de_remplissage'].dt.date <= pd.to_datetime(end_date).date())
                df = df[mask]

            # Déterminer le centre et le zoom de la carte
            if city and city.lower() in self.cities:
                center = [self.cities[city.lower()]['lat'], self.cities[city.lower()]['lon']]
                zoom = self.cities[city.lower()]['zoom']
            else:
                center = [4.0500, 9.7000]
                zoom = 6

            # Créer la carte
            m = folium.Map(
                location=center,
                zoom_start=zoom,
                tiles='cartodbpositron'
            )

            # Filtrer les données et créer les visualisations appropriées
            if quartier:
                df_filtered = df[df['quartier_de_residence'] == quartier]
                # Points simples pour le quartier
                for _, row in df_filtered.iterrows():
                    lat = center[0] + np.random.normal(0, 0.005)
                    lon = center[1] + np.random.normal(0, 0.005)
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=3,
                        color='#c62828',
                        fill=True,
                        fillColor='#c62828',
                        fillOpacity=0.7,
                        popup=f"Quartier: {row['quartier_de_residence']}"
                    ).add_to(m)

            elif arrondissement:
                df_filtered = df[df['arrondissement_de_residence'] == arrondissement]
                # Créer des clusters pondérés par quartier
                quartier_counts = df_filtered.groupby('quartier_de_residence').size()
                for quartier, count in quartier_counts.items():
                    lat = center[0] + np.random.normal(0, 0.01)
                    lon = center[1] + np.random.normal(0, 0.01)
                    radius = np.sqrt(count) * 5  # Taille proportionnelle à la racine carrée du nombre de donneurs
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=radius,
                        color='#c62828',
                        fill=True,
                        fillColor='#c62828',
                        fillOpacity=0.6,
                        popup=f"Quartier: {quartier}<br>Nombre de donneurs: {count}"
                    ).add_to(m)

            elif city:
                df_filtered = df[df['arrondissement_de_residence'].str.contains(city, case=False, na=False)]
                # Créer la carte de chaleur pour la ville
                heat_data = []
                for _, row in df_filtered.iterrows():
                    lat = center[0] + np.random.normal(0, 0.01)
                    lon = center[1] + np.random.normal(0, 0.01)
                    heat_data.append([lat, lon])
                
                plugins.HeatMap(
                    heat_data,
                    radius=15,
                    blur=10,
                    gradient={0.4: '#1a1f3c', 0.65: '#c62828', 1: '#ff5f52'}
                ).add_to(m)

            # Créer les graphiques
            district_df = df['arrondissement_de_residence'].value_counts().reset_index()
            district_df.columns = ['arrondissement', 'nombre']
            district_fig = px.bar(
                district_df,
                x='arrondissement',
                y='nombre',
                title='Répartition des donneurs par arrondissement',
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

            quartier_df = df['quartier_de_residence'].value_counts().reset_index()
            quartier_df.columns = ['quartier', 'nombre']
            quartier_fig = px.bar(
                quartier_df,
                x='quartier',
                y='nombre',
                title='Répartition des donneurs par quartier',
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

            return m._repr_html_(), district_fig, quartier_fig

    def render(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Cartographie de la Répartition", className="mb-4"),
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Filtres", className="card-title"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Ville"),
                                    dcc.Dropdown(
                                        id="city-select",
                                        options=[
                                            {'label': 'Douala', 'value': 'douala'},
                                            {'label': 'Yaoundé', 'value': 'yaounde'},
                                            {'label': 'Bafoussam', 'value': 'bafoussam'}
                                        ],
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
                                    html.Label("Quartier"),
                                    dcc.Dropdown(
                                        id="quartier-select",
                                        placeholder="Sélectionnez un quartier"
                                    )
                                ], md=4)
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Période"),
                                    dcc.DatePickerRange(
                                        id="date-range",
                                        display_format="DD/MM/YYYY"
                                    )
                                ], md=12)
                            ])
                        ])
                    ], className="mb-4")
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Iframe(id="map-container", width="100%", height="600px")
                ], md=12, className="mb-4")
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="district-chart")
                ], md=6),
                dbc.Col([
                    dcc.Graph(id="quartier-chart")
                ], md=6)
            ], className="mb-4")
        ], fluid=True)
