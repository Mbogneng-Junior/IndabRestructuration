import dash_bootstrap_components as dbc
from dash import html

class Card:
    def __init__(self, title, children, footer=None, className=None):
        self.title = title
        self.children = children
        self.footer = footer
        self.className = className

    def render(self):
        return dbc.Card([
            dbc.CardHeader(html.H4(self.title, className="card-title")),
            dbc.CardBody(self.children),
            dbc.CardFooter(self.footer) if self.footer else None
        ], className=f"shadow-sm {self.className if self.className else ''}")
