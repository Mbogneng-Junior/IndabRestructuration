from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from ...services.data.DataService import DataService

# Définir les couleurs
# COLORS = ['#dc3545', '#000000', '#1a1f3c']  # Rouge, Noir, Bleu sombre
COLORS = ['#28A745', '#FFC107', '#DC3545', '#9467bd']  # Vert, Rouge, Bleu, Violet

class DonorProfilesPage:
    def __init__(self):
        self.data_service = DataService()
        self._cache = {}

    def init_callbacks(self, app):
        # @app.callback(
        #     # Output('location-filter', 'options'),
        #     [Input('url', 'pathname')]
        # )
        # def update_location_options(_):
        #     df = self.data_service.get_donor_data()
        #     locations = df['arrondissement_de_residence'].unique()
        #     return [{'label': loc, 'value': loc} for loc in sorted(locations)]
        

        
        @app.callback(
            [Output('cluster-scatter', 'figure'),
             Output('cluster-characteristics', 'children'),
             Output('ideal-donor-profile', 'children')],
            [
            #  Input('location-filter', 'value'),
            #  Input('eligibility-filter', 'value'),
             Input('cluster-slider', 'value')]
        )
        def update_clustering(n_clusters):
            try:
                df = self.data_service.get_donor_data()
                # if location:
                #     df = df[df['arrondissement_de_residence'] == location]
                # if eligibility:
                #     df = df[df['eligibilite_au_don'] == eligibility]
                

                binary_columns = [col for col in df.columns if col.startswith('raison_')]
                nominal_columns = ['niveau_d_etude', 'genre', 'situation_matrimoniale_(sm)', 'religion', 'profession', 'quartier_de_residence', 'arrondissement_de_residence']
                selected_columns = nominal_columns + ['age'] + binary_columns

                df_selected = df[selected_columns].copy()
                df_selected[binary_columns] = df_selected[binary_columns].applymap(lambda x: 0 if x == 'non' else 1)
                le = LabelEncoder()
                for col in nominal_columns:
                    df_selected[col] = le.fit_transform(df_selected[col])
                scaler = StandardScaler()
                df_scaled = scaler.fit_transform(df_selected)

                methods = {
                    'KMeans': KMeans(n_clusters=n_clusters, random_state=42, n_init=10),
                    'Agglomerative': AgglomerativeClustering(n_clusters=n_clusters),
                    'DBSCAN': DBSCAN(eps=1, min_samples=5)
                }

                best_method = None
                best_score = -1
                best_labels = None

                for name, model in methods.items():
                    labels = model.fit_predict(df_scaled)
                    if len(np.unique(labels)) > 1:
                        score = silhouette_score(df_scaled, labels)
                        if score > best_score:
                            best_score = score
                            best_method = name
                            best_labels = labels

                df['Cluster'] = best_labels
                df_selected['cluster'] = best_labels
                ideal_cluster = df_selected.groupby('cluster')[binary_columns].mean().sum(axis=1).idxmin()
                ideal_profile = df[df['Cluster'] == ideal_cluster][selected_columns].mode().iloc[0]
                ideal_display = html.Table([
                    html.Tbody(
                        [html.Tr([
                            html.Td(html.Strong(col.replace('_', ' ').capitalize()), style={"padding": "6px 12px"}),
                            html.Td(f": {ideal_profile[col]}", style={"padding": "6px 12px"})
                        ]) for col in nominal_columns + ['age']
                    ])
                ])


                pca = PCA(n_components=2)
                components = pca.fit_transform(df_scaled)
                viz_df = pd.DataFrame({
                    'PC1': components[:, 0],
                    'PC2': components[:, 1],
                    'Cluster': [f"Groupe {i+1}" for i in best_labels]
                })

                colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33'][:n_clusters]

                scatter_fig = px.scatter(
                    viz_df,
                    x='PC1',
                    y='PC2',
                    color='Cluster',
                    color_discrete_sequence=colors,
                    # title=f'Analyse par Clustering ({best_method})'
                    title=f''
                )

                scatter_fig.update_layout(
                    template='plotly_white',
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=True,
                    legend_title_text='',
                    legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
                )

                cluster_characteristics = []
                for i in range(n_clusters):
                    cluster_df = df[df['Cluster'] == i]
                    cluster_characteristics.extend([
                        html.H6(f"Groupe {i+1}", style={'color': colors[i]}),
                        html.P([
                            f"Taille: {len(cluster_df)} donneurs", html.Br(),
                            f"Âge moyen: {cluster_df['age'].mean():.1f} ans", html.Br(),
                            f"Genre principal: {cluster_df['genre'].mode().iloc[0]}", html.Br(),
                            f"Niveau d'études: {cluster_df['niveau_d_etude'].mode().iloc[0]}", html.Br(),
                            f"Éligibilité: {(cluster_df['eligibilite_au_don'] == 'eligible').mean():.1%}"
                        ])
                    ])

                return scatter_fig, html.Div(cluster_characteristics), ideal_display

            except Exception as e:
                print(f"Erreur dans update_clustering: {str(e)}")
                fig = go.Figure()
                fig.add_annotation(text="Erreur lors du clustering", x=0.5, y=0.5, showarrow=False)
                return fig, html.Div("Erreur dans les caractéristiques"), html.Div("Erreur profil idéal")

        @app.callback(
            [Output('age-distribution', 'figure'),
             Output('religion-distribution', 'figure'),
            #  Output('eligibility-distribution', 'figure'),
             Output('education-distribution', 'figure'),
             Output('marital-distribution', 'figure'),
             Output('gender-distribution', 'figure')],
            [
            # Input('location-filter', 'value'),
            #  Input('eligibility-filter', 'value')
                Input('url', 'pathname')
            ]
        )
        def update_graphs(_):
            df = self.data_service.get_donor_data()

            # if location:
            #     df = df[df['arrondissement_de_residence'] == location]
            # if eligibility:
            #     df = df[df['eligibilite_au_don'] == eligibility]

            # Age distribution
            age_fig = px.histogram(df, x='age', nbins=20, title='Distribution par âge', color='eligibilite_au_don', barmode='stack',
                                   color_discrete_sequence=COLORS)

            # Religion distribution
            religion_fig = px.bar(df, x='religion', title='Répartition par religion', color='eligibilite_au_don', barmode='stack',
                                  color_discrete_sequence=COLORS)

            # Education distribution
            education_fig = px.bar(df, x='niveau_d_etude', title="Répartition par niveau d'étude", color='eligibilite_au_don', barmode='stack',
                                   color_discrete_sequence=COLORS)

            # Marital status distribution
            marital_fig = px.bar(df, x='situation_matrimoniale_(sm)', title='Répartition par statut matrimonial', color='eligibilite_au_don', barmode='stack',
                                 color_discrete_sequence=COLORS)

            # Gender distribution as bar chart
            gender_fig = px.bar(df, x='genre', title='Répartition par genre', color='eligibilite_au_don', barmode='stack',
                                color_discrete_sequence=COLORS)

            for fig in [age_fig, religion_fig, education_fig, marital_fig, gender_fig]:
                fig.update_layout(
                    template='plotly_white',
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis_tickangle=-45
                )

            return age_fig, religion_fig, education_fig, marital_fig, gender_fig


    def _prepare_clustering_data(self, df):
        """Prépare les données pour le clustering"""
        try:
            # Sélectionner les colonnes numériques et catégorielles pertinentes
            numeric_cols = ['age']
            
            # Colonnes catégorielles principales
            categorical_cols = [
                'genre', 
                'niveau_d_etude', 
                'religion', 
                'situation_matrimoniale_(sm)',
                'profession'
            ]
            
            # Colonnes de santé (convertir en 0/1)
            health_cols = [
                'raison_indisponibilité__[est_sous_anti-biothérapie__]',
                'raison_indisponibilité__[taux_d\'hémoglobine_bas_]',
                'raison_indisponibilité__[date_de_dernier_don_<_3_mois_]',
                'raison_indisponibilité__[ist_récente_(exclu_vih,_hbs,_hcv)]',
                'raison_de_non-eligibilité_totale__[porteur(hiv,hbs,hcv)]',
                'raison_de_non-eligibilité_totale__[opéré]',
                'raison_de_non-eligibilité_totale__[drepanocytaire]',
                'raison_de_non-eligibilité_totale__[diabétique]',
                'raison_de_non-eligibilité_totale__[hypertendus]',
                'raison_de_non-eligibilité_totale__[asthmatiques]',
                'raison_de_non-eligibilité_totale__[cardiaque]'
            ]
            
            # Créer une copie du DataFrame pour éviter les modifications sur l'original
            df_prep = df.copy()
            
            # Convertir l'éligibilité en valeur numérique
            df_prep['eligibilite_num'] = (df_prep['eligibilite_au_don'] == 'eligible').astype(int)
            
            # Créer des variables dummy pour les colonnes catégorielles
            df_encoded = pd.get_dummies(df_prep[categorical_cols])
            
            # Ajouter les colonnes numériques
            for col in numeric_cols:
                df_encoded[col] = df_prep[col]
            
            # Ajouter l'éligibilité numérique
            df_encoded['eligibilite'] = df_prep['eligibilite_num']
            
            # Ajouter les colonnes de santé
            for col in health_cols:
                if col in df_prep.columns:
                    # Convertir les valeurs en 0/1
                    col_name = col.split('__')[-1].replace('[', '').replace(']', '')
                    df_encoded[col_name] = df_prep[col].fillna(0).map({'oui': 1, 'non': 0}).astype(int)
            
            # Standardiser les données
            scaler = StandardScaler()
            df_scaled = pd.DataFrame(scaler.fit_transform(df_encoded), columns=df_encoded.columns)
            
            return df_scaled
            
        except Exception as e:
            print(f"Erreur dans prepare_clustering_data: {str(e)}")
            raise e

    def _create_profile_interpretation(self, df, clusters):
        """Crée un tableau d'interprétation des profils"""
        interpretation_table = []
        
        for i in range(len(np.unique(clusters))):
            cluster_df = df[df['Cluster'] == i]
            
            # Caractéristiques principales
            age_mean = cluster_df['age'].mean()
            age_std = cluster_df['age'].std()
            gender_main = cluster_df['genre'].mode().iloc[0]
            education_main = cluster_df['niveau_d_etude'].mode().iloc[0]
            religion_main = cluster_df['religion'].mode().iloc[0]
            eligibility_rate = (cluster_df['eligibilite_au_don'] == 'eligible').mean()
            
            # Problèmes de santé principaux
            health_cols = [col for col in cluster_df.columns if 'raison' in col]
            health_issues = []
            for col in health_cols:
                count = cluster_df[col].map({'oui': 1, 'non': 0}).sum()
                if count > 0:
                    issue = col.split('__')[-1].replace('[', '').replace(']', '').replace('_', ' ')
                    health_issues.append(f"{issue} ({count})")
            
            # Créer le contenu des cellules avec des éléments HTML
            profile_content = [
                html.Span([
                    f"Age: {age_mean:.1f}±{age_std:.1f} ans",
                    html.Br(),
                    f"Genre: {gender_main}",
                    html.Br(),
                    f"Éducation: {education_main}",
                    html.Br(),
                    f"Religion: {religion_main}"
                ])
            ]
            
            health_content = [
                html.Span([
                    *[html.Span([issue, html.Br()]) for issue in health_issues[:3]]
                ]) if health_issues else "Aucun problème majeur"
            ]
            
            interpretation_table.append({
                "Cluster": f"Cluster {i+1}",
                "Taille": len(cluster_df),
                "Profil": profile_content,
                "Éligibilité": f"{eligibility_rate:.1%}",
                "Problèmes de santé": health_content
            })
        
        # Créer le tableau HTML
        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Cluster"),
                    html.Th("Taille"),
                    html.Th("Profil type"),
                    html.Th("Taux d'éligibilité"),
                    html.Th("Problèmes de santé principaux")
                ], className="table-dark")
            ),
            html.Tbody([
                html.Tr([
                    html.Td(row["Cluster"]),
                    html.Td(row["Taille"]),
                    html.Td(row["Profil"]),
                    html.Td(row["Éligibilité"]),
                    html.Td(row["Problèmes de santé"])
                ]) for row in interpretation_table
            ])
        ], bordered=True, hover=True, responsive=True)
        
        return table

    def _update_graphs(self):
        df = self.data_service.get_donor_data()
        
        try:
            # Appliquer les filtres
            # if location:
            #     df = df[df['arrondissement_de_residence'] == location]
            # if eligibility:
            #     df = df[df['eligibilite_au_don'] == eligibility]
            
            # Distribution par âge
            age_fig = px.histogram(
                df,
                x='age',
                nbins=20,
                title='Distribution par âge',
                color_discrete_sequence=[COLORS[0]]  # Rouge
            )
            
            # Distribution par religion
            religion_counts = df['religion'].value_counts().reset_index()
            religion_counts.columns = ['Religion', 'Nombre']
            religion_fig = px.bar(
                religion_counts,
                x='Religion',
                y='Nombre',
                title='Répartition par religion',
                color_discrete_sequence=[COLORS[1]]  # Noir
            )
            
            # Distribution par éligibilité
            eligibility_counts = df['eligibilite_au_don'].value_counts().reset_index()
            eligibility_counts.columns = ['Statut', 'Nombre']
            eligibility_fig = px.bar(
                eligibility_counts,
                x='Statut',
                y='Nombre',
                title="Répartition par éligibilité",
                color_discrete_sequence=[COLORS[2]]  # Bleu sombre
            )
            
            # Distribution par niveau d'étude
            education_counts = df['niveau_d_etude'].value_counts().reset_index()
            education_counts.columns = ['Niveau', 'Nombre']
            education_fig = px.bar(
                education_counts,
                x='Niveau',
                y='Nombre',
                title="Répartition par niveau d'étude",
                color_discrete_sequence=[COLORS[0]]  # Rouge
            )
            
            # Distribution par statut matrimonial
            marital_counts = df['situation_matrimoniale_(sm)'].value_counts().reset_index()
            marital_counts.columns = ['Statut', 'Nombre']
            marital_fig = px.bar(
                marital_counts,
                x='Statut',
                y='Nombre',
                title='Répartition par statut matrimonial',
                color_discrete_sequence=[COLORS[1]]  # Noir
            )
            
            # Distribution par genre (pie chart)
            gender_counts = df['genre'].value_counts().reset_index()
            gender_counts.columns = ['Genre', 'Nombre']
            gender_fig = px.pie(
                gender_counts,
                names='Genre',
                values='Nombre',
                title='Répartition par genre',
                color_discrete_sequence=COLORS  # Utiliser toutes les couleurs
            )
            
            # Mettre à jour le layout de tous les graphiques
            for fig in [age_fig, religion_fig, eligibility_fig, education_fig, marital_fig]:
                fig.update_layout(
                    template='plotly_white',
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False,
                    xaxis_tickangle=-45
                )
            
            gender_fig.update_layout(
                template='plotly_white',
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            return age_fig, religion_fig, eligibility_fig, education_fig, marital_fig, gender_fig
            
        except Exception as e:
            print(f"Erreur dans update_graphs: {str(e)}")
            # Retourner des graphiques vides en cas d'erreur
            empty_figs = []
            for _ in range(6):
                fig = go.Figure()
                fig.add_annotation(
                    text="Erreur lors du chargement des données",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
                empty_figs.append(fig)
            return tuple(empty_figs)

    def render(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Profils des Donneurs", className="mb-4")
                ])
            ]),
            
            # Filtres
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.Strong("Filtres")),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Ville"),
                                    dcc.Dropdown(
                                        id='ville-filter',
                                        placeholder="Sélectionner une ville",
                                        className="mb-2",
                                        style={'zIndex': 9999}
                                    )
                                ], md=4),
                                dbc.Col([
                                    html.Label("Arrondissement"),
                                    dcc.Dropdown(
                                        id='arrondissement-filter',
                                        options=[
                                            {'label': 'Éligible', 'value': 'eligible'},
                                            {'label': 'Non éligible', 'value': 'ineligible'}
                                        ],
                                        placeholder="Sélectionner un Arrondissement",
                                        className="mb-2"
                                    )
                                ], md=4),
                                dbc.Col([
                                    html.Label("Période"),
                                    dcc.DatePickerRange(
                                        id="date-range",
                                        display_format="DD/MM/YYYY"
                                    )
                                ], md=4),
                            ])
                        ]),
                        dbc.Row([
                            # dbc.Col([
                            #     html.Label("Localisation"),
                            #     dcc.Dropdown(
                            #         id='location-filter',
                            #         placeholder="Sélectionner un arrondissement",
                            #         className="mb-2",
                            #         style={'zIndex': 9999}
                            #     )
                            # ], md=4),
                            # dbc.Col([
                            #     html.Label("Statut d'éligibilité"),
                            #     dcc.Dropdown(
                            #         id='eligibility-filter',
                            #         options=[
                            #             {'label': 'Éligible', 'value': 'eligible'},
                            #             {'label': 'Non éligible', 'value': 'ineligible'}
                            #         ],
                            #         placeholder="Sélectionner un statut",
                            #         className="mb-2"
                            #     )
                            # ], md=4),
                            dbc.Col([
                                html.Label("Nombre de groupes"),
                                dcc.Slider(
                                    id='cluster-slider',
                                    min=2,
                                    max=6,
                                    step=1,
                                    value=3,
                                    marks={i: str(i) for i in range(2, 7)},
                                    className="mt-2"
                                )
                            ], md=4)
                        ])
                    ], className="mb-4")
                ])
            ]),
            
            # Section Clustering
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Regroupement des partcipants en profils similaires"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([dcc.Graph(id='cluster-scatter', config={'displayModeBar': False})], md=8),
                                dbc.Col([html.Div(id='cluster-characteristics', className="cluster-analysis")], md=4)
                            ])
                        ])
                    ], className="chart-card mb-4")
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Donneur Idéal"),
                        dbc.CardBody([
                            html.Div(id='ideal-donor-profile')
                        ])
                    ], className="chart-card mb-4")
                ], md=4)
            ]),

            # Graphiques de distribution
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribution par âge"),
                        dbc.CardBody([dcc.Graph(id='age-distribution', config={'displayModeBar': False})])
                    ], className="chart-card mb-4")], md=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribution par genre"),
                        dbc.CardBody([dcc.Graph(id='gender-distribution', config={'displayModeBar': False})])
                    ], className="chart-card mb-4")], md=6),

            ], className="mb-4"),


            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribution par religion"),
                        dbc.CardBody([dcc.Graph(id='religion-distribution', config={'displayModeBar': False})])
                    ], className="chart-card mb-4" )], md=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribution par niveau d'étude"),
                        dbc.CardBody([dcc.Graph(id='education-distribution', config={'displayModeBar': False})])
                    ], className="chart-card mb-4" )], md=6),

            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribution par statut matrimonial"),
                        dbc.CardBody([dcc.Graph(id='marital-distribution', config={'displayModeBar': False})])
                    ], className="chart-card mb-4")], md=6)
            ], className="mb-4")
           
        ], fluid=True)