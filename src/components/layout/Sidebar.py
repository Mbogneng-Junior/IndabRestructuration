import dash_bootstrap_components as dbc
from dash import html
import os

# Importer le fichier CSS
current_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(current_dir, 'Sidebar.css')

class Sidebar:
    def __init__(self):
        pass
        
    def render(self):
        """Rendu de la barre latérale"""
        return html.Div([
            # Header
            html.Div([
                html.Img(src="/assets/images/logo.png", className="sidebar-logo"),
                
            ], className="sidebar-header"),
            
            # Body - Menu de navigation
            html.Div([
                html.Ul([
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-tachometer-alt"), "Tableau de bord"],
                            href="/",
                            active="exact",
                            className="nav-link"
                        )
                    ),
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-map-marked-alt"), "Cartographie"],
                            href="/mapping",
                            active="exact",
                            className="nav-link"
                        )
                    ),
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-users"), "Profils Donneurs"],
                            href="/donor-profiles",
                            active="exact",
                            className="nav-link"
                        )
                    ),
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-chart-line"), "Analyse Campagnes"],
                            href="/campaign-analysis",
                            active="exact",
                            className="nav-link"
                        )
                    ),
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-heartbeat"), "Santé & Éligibilité"],
                            href="/health-analysis",
                            active="exact",
                            className="nav-link"
                        )
                    ),
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-check-circle"), "Prédiction Éligibilité"],
                            href="/eligibility-prediction",
                            active="exact",
                            className="nav-link"
                        )
                    ),
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-sync"), "Rétention Donneurs"],
                            href="/donor-retention",
                            active="exact",
                            className="nav-link"
                        )
                    ),
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-comments"), "Analyse Feedback"],
                            href="/feedback-analysis",
                            active="exact",
                            className="nav-link"
                        )
                    )
                ], className="nav-menu")
            ], className="sidebar-body"),
            
            # Footer
            html.Div([
                html.P("Équipe HOPE", className="mb-1"),
                html.P("2025")
            ], className="sidebar-footer")
        ], className="sidebar")