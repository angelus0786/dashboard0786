import dash
from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go

dash.register_page(__name__, path='/')
#cargar datos
try:
   df = pd.read_csv("01survey.csv",sep=',')
except Exception as e:
    print(f"Error al cargar el archivo: {e}")

df_mark1 = df.copy()
df_mark1.item =df_mark1.item.replace([81,82,83,84,85,86,87,88,89,90,91],[59,60,61,62,63,64,65,66,67,68,69])
df_mark1.item =df_mark1.item.replace([48,49,50,51,52,53,54,55,56,57,58],[59,60,61,62,63,64,65,66,67,68,69])

df_pivote = pd.pivot_table(df_mark1, index=['userId'],columns=['item'], values=['value'] )
#conversion de pivote a dataframe
df_pesp = pd.DataFrame(df_pivote)
df_pesp = df_pivote.rename(columns={59:'carrera',60:'semestre',61:'genero',62:'modalidad',
       63:'edad', 64:'edo_civil',65:'situacion_lab',66:'mgradoestudio_padre',67:'mgradestudio_madre',
       68:'relacion_amigos', 69:'Pareja'})

#contar modalidad
modalidad_1_count = (df_pivote['value',62].values==1.0).sum()
modalidad_2_count = df_pivote['value',62].value_counts()[2.0]

#print(dash.page_registry)
conteo_genero = df_pesp['value','genero'].value_counts().sort_index()
#print(f'conteo genero2: {df_pesp['value','genero'].value_counts().sort_index()}')

total_hombres = conteo_genero[1]
total_mujeres = conteo_genero[2]
total_estudiantes = df_mark1['userId'].nunique()

#print(f"conteo genero: {conteo_genero}")


card_estudiante = dbc.Card([
    dbc.CardHeader("Indicador Estudiantes", className="card-header text-center fw-bold"),
    dbc.CardBody(
        [
            html.H5("Número de Estudiantes", className="card-title text-center"),
            html.P(f'{df["userId"].nunique()}',
                className="card-text text-center display-3 fw-bold",
                style={'font-size': '2rem'},
            ),
        ]
    ),
],className="card text-bg-success mb-3",
style={'maxWidth': '18rem'})

card_curso =dbc.Card([
    dbc.CardHeader("Indicador Curso", className="card-header text-center fw-bold"),
    dbc.CardBody(
        [
            html.H5("Total Cursos", className="card-title text-center"),
            html.P( f'{df["course"].nunique()}',
                className="card-text text-center display-3 fw-bold",
                style={'font-size': '2rem'},
            ),
        ]
    ),
],className="card text-bg-danger mb-3",
style={'maxWidth': '18rem'})

card_semestre = dbc.Card([
    dbc.CardHeader("Indicador Semestres" , className="card-header text-center fw-bold"),
    dbc.CardBody(
        [
            html.H5("Total Semestres", className="card-title text-center"),
            html.P( f'{len(df_pesp['value','semestre'].unique())}',
                className="card-text text-center display-3 fw-bold",
                style={'font-size': '2rem'},
            ),
        ]
    ),
],className="card text-bg-warning mb-3",
style={'maxWidth': '18rem'})

card_modalidad = dbc.Card([
    dbc.CardHeader("Indicador Modalidad", className="card-header text-center fw-bold"),
    dbc.CardBody(
        [
            html.H5("Escolarizado / Sabatino", className="card-title text-center"),
            html.P(f'{modalidad_1_count}'+
                   '/'+
                   f'{modalidad_2_count}',
             className="card-text text-center display-3 fw-bold",
                style={'font-size': '2rem'},
            )
        ]
    ),
],className="card text-bg-info mb-3",
style={'maxWidth': '18rem'})

#grafico para mujeres
gauge_mujeres = go.Figure(
    data = [go.Indicator(
    mode="gauge+number",
    value=total_mujeres,
    title={'text': "Mujeres"},
    gauge={
        'axis': {'range': [0, total_estudiantes]},
        'bar': {'color': "#FF7F50"},
        'steps': [
            {'range': [0, total_mujeres], 'color': "lightgreen"},
            {'range': [total_mujeres, total_estudiantes], 'color': "lightgrey"}
        ]
    }
)],
layout=go.Layout(
    #title="Mujeres",
    height=300,
    margin=dict(l=20, r=20, t=40, b=20),
))
#grafico para hombres
gauge_hombres = go.Figure(
    data = [go.Indicator(
    mode="gauge+number",
    value=total_hombres,
    title={'text': "Hombres"},
    gauge={
        'axis': {'range': [0, total_estudiantes]},
        'bar': {'color': "#FF7F50"},
        'steps': [
            {'range': [0, total_hombres], 'color': "lightblue"},
            {'range': [total_hombres, total_estudiantes], 'color': "lightgrey"}
        ]
    }
)],
layout=go.Layout(
    #title="Hombres",
    height=300,
    margin=dict(l=20, r=20, t=40, b=20),
))


layout = dbc.Container(
    [
        html.H1("Analiticas de Estudiantes ITS Perote", className="text-center my-4",
                 style={'fontSize': '36px', 'fontWeight': 'bold'}),
        html.Hr(), 
            dbc.Row([
            dbc.Col(card_estudiante, width=3 ,style={"display": "flex", "flexDirection": "column", "height": "100%"}),
            dbc.Col(card_curso, width=3, style={"display": "flex", "flexDirection": "column", "height": "100%"}),
            dbc.Col(card_semestre, width=3, style={"display": "flex", "flexDirection": "column", "height": "100%"}),
            dbc.Col(card_modalidad, width=3, style={"display": "flex", "flexDirection": "column", "height": "100%"}),
            ]),
            dbc.Row([
                    dbc.Col(
                    html.H1("Indicadores de Género", className="text-center my-4"),
                    width=12
                    )
                   
            ]),
            dbc.Row([
                  dbc.Col(
                  dbc.Card(
                        dbc.CardBody(
                            children=[
                            html.H4("KPI Mujeres", className="card-title"),
                            dcc.Graph(id='graph_mujeres',figure=gauge_mujeres)
                            ]
                        ),className="mb-4 text-center",
                                style={"background-color": "#FF7F50", "color": "white"}
                  ),width=6  
                ),
                dbc.Col(
                  dbc.Card(
                        dbc.CardBody(
                            children=[
                            html.H4("KPI Hombres", className="card-title"),
                            dcc.Graph(id='graph_hombres',figure=gauge_hombres)
                            ]
                        ),className="mb-4 text-center",
                                style={"background-color": "#1E90FF", "color": "white"}
                  ),width=6  
                ),
             ])
    ],
    fluid=True,
    className="container-fluid")  # Asegura que se adapten bien los estilos de Bootstrap

