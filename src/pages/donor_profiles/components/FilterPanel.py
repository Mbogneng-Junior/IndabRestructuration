from dash import html
import dash_bootstrap_components as dbc

class FilterPanel:
    def __init__(self):
        pass
        
    def render(self):
        return html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Filtres", className="card-title"),
                    html.P("Les filtres seront implémentés ici.")
                ])
            ])
        ])
