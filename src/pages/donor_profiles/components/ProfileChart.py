from dash import html
import dash_bootstrap_components as dbc

class ProfileChart:
    def __init__(self, data_service):
        self.data_service = data_service
        
    def render(self):
        return html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Graphique des Profils", className="card-title"),
                    html.P("Le graphique des profils sera implémenté ici.")
                ])
            ])
        ])
