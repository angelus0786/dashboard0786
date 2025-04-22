import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import warnings
warnings.filterwarnings("ignore")
import dash_auth 
import os



SIDEBAR_STYLE = {
    'position':'fixed',
    'top':0,
    'left':0,
    'bottom':0,
    'width':'12rem',  
    'padding':'2rem 1rem',
    'backgroundColor':'#2b2b2b',
    'color':'#cfcfcf',
    'fontSize':'23px',
    'boxShadow':'5px 5px 5px 5px lightgrey'
}

CONTENT_STYLE = {
    'marginLeft':'15rem',
    'marginRight':'2rem',
    'padding':'2rem 1rem'
}

#crear lista de usuarios
Lista_usuarios = [
    ['admin','admin'], #usuario y contraseña
    ['user','007']
]

app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           suppress_callback_exceptions=True
           )
server = app.server 
#creacion de autenticacion
auth = dash_auth.BasicAuth(
    app,
    Lista_usuarios
)



sidebar = html.Div(
    [
        html.H1(f'Dashboard',style={'fontSize':'32px','fontWeight':'bold'}),
        html.Hr(),
        html.H2('Menú', className='lead',style={'fontSize':'26px'}),
        html.Hr(),
        dbc.Nav(
            [
                 dbc.NavLink("Inicio",href="/",active='exact'),
                 dbc.NavLink("Miradas",href="/miradas",active='exact'),
                 #dbc.NavLink("Clusters",href="/cluster",active='exact')
                # dbc.NavLink(f"{page['name']}",href=page["relative_path"],active='exact')
               # for page in dash.page_registry.values()               
            ],
            vertical=True,
            pills=True
        ),
    ],
    style=SIDEBAR_STYLE)

content = html.Div([
    dcc.Location(id='url',refresh=False),
    dash.page_container
],style=CONTENT_STYLE)

#layout principal
app.layout = html.Div([sidebar,content])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    prevent_initial_call=True
)

def  render_page_content(pathname):
    if pathname == '/':
        return dash.page_registry['home']['layout']
    elif pathname == '/home':
        return dash.page_registry['home']['layout']
    elif pathname == '/miradas':
        return dash.page_registry['miradas']['layout']
    elif pathname == '/cluster':
        return dash.page_registry['cluster']['layout']
    # Add a default case if needed
   # return html.Div([
    #    html.H3(f"You are on the page: {pathname}")
   # ])
    

if __name__ == '__main__':
    #app.run(debug=True)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)