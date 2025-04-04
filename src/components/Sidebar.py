import dash_bootstrap_components as dbc
from dash import html
from datetime import datetime

class Sidebar:
    def __init__(self):
        pass
        
    def render(self):
        """Rendu de la barre latérale"""
        return html.Div([
            # Header
            html.Div([
                html.Img(src="/assets/images/logo.png", className="sidebar-logo"),
                html.H1("IndabaX", className="sidebar-title")
            ], className="sidebar-header"),
            
            # Body - Menu de navigation
            html.Div([
                html.Ul([
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-home"), "Accueil"],
                            href="/",
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
                            [html.I(className="fas fa-heartbeat"), "Analyse Santé"],
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
                html.P(datetime.now().strftime("%Y"), className="mb-0")
            ], className="sidebar-footer")
        ], className="sidebar")

"""
return html.Div([
            # Header
            html.Div([
                html.Img(src="/assets/images/logo.png", className="sidebar-logo"),
                html.H1("IndabaX", className="sidebar-title")
            ], className="sidebar-header"),
            
            # Body - Menu de navigation
            html.Div([
                html.Ul([
                    html.Li(
                        dbc.NavLink(
                            [html.I(className="fas fa-home"), "Accueil"],
                            href="/",
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
                            [html.I(className="fas fa-heartbeat"), "Analyse Santé"],
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
                html.P(datetime.now().strftime("%Y"), className="mb-0")
            ], className="sidebar-footer")
        ], className="sidebar")

"""