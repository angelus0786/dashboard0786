import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import warnings
warnings.filterwarnings("ignore")
import dash_auth 
import os
import flask

#Lista de usuarios
Lista_usuarios = [
    ['admin','admin'], #usuario y contraseña
    ['user','007']
]

#Estilos principales
SIDEBAR_STYLE = {
    'padding': '2rem 1rem',
    'backgroundColor': '#2b2b2b',
    'color': '#cfcfcf',
    'fontSize': '23px',
    'boxShadow': '5px 5px 5px lightgrey',
    'height': '100vh' 
}

CONTENT_STYLE = {
    'padding': '2rem 1rem'   
}

# Inicialización de la app
app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           suppress_callback_exceptions=True
           )
#autenticacion
auth = dash_auth.BasicAuth(app,Lista_usuarios)

# Sidebar como offcanvas para móviles
offcanvas = html.Div([
    dbc.Button("☰ Menú", id="open-offcanvas", n_clicks=0, className="d-md-none mb-3", color="secondary"),
    dbc.Offcanvas(
        [
            html.H2('Dashboard', style={'fontWeight': 'bold'}),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink("Inicio", href="/", active="exact"),
                    dbc.NavLink("Miradas", href="/analisisxestudiante", active="exact"),
                    dbc.NavLink("Clusters", href="/clusters", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        id="offcanvas",
        is_open=False,
        placement="start",
        style={"backgroundColor": "#2b2b2b", "color": "#cfcfcf"}
    )
])

# Sidebar fijo para pantallas medianas y grandes
sidebar = html.Div(
    [
        html.H2("Dashboard", style={'fontWeight': 'bold'}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Inicio", href="/", active="exact"),
                dbc.NavLink("Miradas", href="/analisisxestudiante", active="exact"),
                dbc.NavLink("Clusters", href="/clusters", active="exact"),
            ],
            vertical=True,
            pills=True
        ),
    ],
    className="d-none d-md-block",
    style=SIDEBAR_STYLE
)

#contenido principal
content = html.Div([
    dcc.Location(id='url',refresh=False),
    dash.page_container
],style=CONTENT_STYLE)

#layout principal
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([sidebar, offcanvas], md=3),
        dbc.Col(content, md=9)
    ])
], fluid=True)

# Callback para abrir el menú offcanvas
@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    prevent_initial_call=True
)
def toggle_offcanvas(n_clicks):
    return True
  

if __name__ == '__main__':
  #  app.run(debug=True)     #comentar para subir al servidor
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)