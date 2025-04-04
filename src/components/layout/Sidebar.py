import dash_bootstrap_components as dbc
from dash import html
import os

# Importer le fichier CSS
current_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(current_dir, 'Sidebar.css')

class Sidebar:
    def render(self):
        """Rendu de la barre latérale"""
        return html.Div([
            # Logo et titre
            html.Div([
                html.Img(src="/assets/images/logo.png", className="logo"),
                html.H1("Indaba", className="brand-text")
            ], className="brand"),
            
            # Navigation
            html.Nav([
                dbc.Nav([
                    dbc.NavLink([
                        html.I(className="fas fa-home me-2"),
                        "Accueil"
                    ], href="/", active="exact"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-users me-2"),
                        "Profils Donneurs"
                    ], href="/donor-profiles", active="exact"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-chart-line me-2"),
                        "Analyse Campagnes"
                    ], href="/campaign-analysis", active="exact"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-heartbeat me-2"),
                        "Analyse Santé"
                    ], href="/health-analysis", active="exact"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-sync me-2"),
                        "Rétention Donneurs"
                    ], href="/retention", active="exact"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-check-circle me-2"),
                        "Prédiction Éligibilité"
                    ], href="/prediction", active="exact"),
                    
                    dbc.NavLink([
                        html.I(className="fas fa-comment me-2"),
                        "Feedback"
                    ], href="/feedback", active="exact")
                ], vertical=True, pills=True)
            ], className="nav-menu")
        ], className="sidebar-content")
