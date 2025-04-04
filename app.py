from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from src.components.layout.Sidebar import Sidebar
from src.pages.home.HomePage import HomePage
from src.pages.donor_profiles.DonorProfilesPage import DonorProfilesPage
from src.pages.campaign_analysis.CampaignAnalysisPage import CampaignAnalysisPage
from src.pages.health_analysis.HealthAnalysisPage import HealthAnalysisPage
from src.pages.donor_retention.DonorRetentionPage import DonorRetentionPage
from src.pages.feedback.FeedbackPage import FeedbackPage
from src.pages.prediction.PredictionPage import PredictionPage

# Variables CSS personnalisées
CUSTOM_STYLE = {
    'background': '#f4f6f9',
    'font-family': 'Poppins, sans-serif'
}

# Initialisation de l'application
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css'
    ],
    suppress_callback_exceptions=True
)

# Création des composants principaux
sidebar = Sidebar()
home_page = HomePage()
donor_profiles_page = DonorProfilesPage()
campaign_analysis_page = CampaignAnalysisPage()
health_analysis_page = HealthAnalysisPage()
donor_retention_page = DonorRetentionPage()
feedback_page = FeedbackPage()
prediction_page = PredictionPage()

# Initialisation des callbacks
home_page.init_callbacks(app)
donor_profiles_page.init_callbacks(app)
health_analysis_page.init_callbacks(app)
campaign_analysis_page.init_callbacks(app)
donor_retention_page.init_callbacks(app)
feedback_page.init_callbacks(app)
prediction_page.init_callbacks(app)

# Layout principal de l'application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        # Sidebar
        html.Div([
            sidebar.render()
        ], className="sidebar"),
        
        # Contenu principal
        html.Div([
            html.Div(id='page-content')
        ], className="content")
    ]),
], style=CUSTOM_STYLE)

# Style CSS personnalisé
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Indaba</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {
                margin: 0;
                font-family: 'Poppins', sans-serif;
                background-color: #f8f9fa;
            }
            
            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                height: 100vh;
                width: 16rem;
                z-index: 1000;
            }
            
            .content {
                margin-left: 16rem;
                padding: 2rem;
                width: calc(100% - 16rem);
            }
            
            /* Styles de base */
            :root {
                --primary: #FF4136;
                --secondary: #333333;
                --success: #28a745;
                --info: #17a2b8;
                --warning: #ffc107;
                --danger: #dc3545;
                --light: #f8f9fa;
                --dark: #343a40;
                --white: #ffffff;
                --gray-100: #f8f9fa;
                --gray-200: #e9ecef;
                --gray-300: #dee2e6;
                --gray-400: #ced4da;
                --gray-500: #adb5bd;
                --gray-600: #6c757d;
                --gray-700: #495057;
                --gray-800: #343a40;
                --gray-900: #212529;
            }
            
            /* Style des cartes */
            .card {
                border: none;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                margin-bottom: 1.5rem;
            }
            
            .card-header {
                background-color: var(--white);
                border-bottom: 1px solid var(--gray-200);
                padding: 1.5rem;
            }
            
            .card-body {
                padding: 1.5rem;
            }
            
            /* Style des boutons */
            .btn {
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: 500;
            }
            
            .btn-primary {
                background-color: var(--primary);
                border-color: var(--primary);
            }
            
            .btn-primary:hover {
                background-color: #ff1f1f;
                border-color: #ff1f1f;
            }
            
            /* Style des inputs */
            .form-control {
                border-radius: 8px;
                border: 1px solid var(--gray-300);
                padding: 0.5rem 1rem;
            }
            
            .form-control:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 0.2rem rgba(255, 65, 54, 0.25);
            }
            
            /* Style des dropdowns */
            .dropdown-menu {
                border: none;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }
            
            /* Style des tableaux */
            .table {
                border-radius: 8px;
                overflow: hidden;
            }
            
            .table thead th {
                background-color: var(--gray-100);
                border-bottom: 1px solid var(--gray-200);
                font-weight: 600;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .sidebar {
                    width: 100%;
                    height: auto;
                    position: relative;
                }
                
                .content {
                    margin-left: 0;
                    width: 100%;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Callback pour la navigation
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/donor-profiles':
        return donor_profiles_page.render()
    elif pathname == '/campaign-analysis':
        return campaign_analysis_page.render()
    elif pathname == '/health-analysis':
        return health_analysis_page.render()
    elif pathname == '/retention':
        return donor_retention_page.render()
    elif pathname == '/feedback':
        return feedback_page.render()
    elif pathname == '/prediction':
        return prediction_page.render()
    else:
        return home_page.render()

if __name__ == '__main__':
    app.run_server(debug=True)
