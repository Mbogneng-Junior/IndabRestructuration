from dash import html
import dash_bootstrap_components as dbc

class DonorTable:
    def __init__(self, data_service):
        self.data_service = data_service
        
    def render(self):
        return html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Table des Donneurs", className="card-title"),
                    html.P("La table des donneurs sera implémentée ici.")
                ])
            ])
        ])
