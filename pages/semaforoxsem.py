import dash
from dash import dcc, html, Input, Output,State,ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np  
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from sklearn import preprocessing
from kmodes.kprototypes import KPrototypes
import math
#%matplotlib inline
import warnings
warnings.filterwarnings('ignore')
import os

# Obtener la ruta absoluta del directorio actual (es decir, 'pages')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Construir la ruta absoluta al archivo CSV dentro de 'data'
csv_path = os.path.join(BASE_DIR,  'data', '02survey.csv')
csv_path1 = os.path.join(BASE_DIR,  'data', '01 users1.csv')
csv_path2 = os.path.join(BASE_DIR,  'data', '01 assignament.csv')
csv_path3 = os.path.join(BASE_DIR,  'data', '02 assignament.csv')

# Cargar el dataset
df_survey =pd.read_csv(csv_path,sep=',')  
# Relacion de cantidad de estudiantes por semestres (ciclo)
df_survey[df_survey['item']==60]['value'].value_counts()
# Seleccion de variables utiles y pasando las variables a minuscula
survey_2=df_survey[['userId','item','value','period']]
survey_2.columns=survey_2.columns.str.lower()
# Seleccion de estudiantes finales a partir de 1*,2*,3*,4*, 5* y 6* Semestre(ciclo)
estudiantes=survey_2[(survey_2['item']==60) & (survey_2['value'].isin([4,5,6])) ]['userid']
survey_3=survey_2[survey_2['userid'].isin(estudiantes)]
# Obtener el índice del mayor valor de 'periodo' por 'userid item'
idx = survey_3.groupby(['userid','item'])['period'].idxmax()
# Filtrar el DataFrame usando esos índices
survey_4 = survey_3.loc[idx].reset_index(drop=True)
# Eliminando la variable period
survey_4.drop('period',axis=1,inplace=True)
# Reestructurando el data set
survey4_wider = survey_4.pivot(index='userid', columns='item', values='value').reset_index()
survey4_wider.columns.name = None
# Por ultimo la encuesta se realizo a modalidad mixta
survey4_wider[62]=2
# Data set matricula
mat=pd.read_csv(csv_path1,sep=',')
# Realizando el join entre survey y mattricula para obtener el username de cada userid
survey5_wider=pd.merge(survey4_wider, mat[['id','username']], left_on='userid', right_on='id', how='inner')
assign2024=pd.read_csv(csv_path2,sep=',')
# Seleccion de variables
assign2024=assign2024[['userna','grade']]
assign2025=pd.read_csv(csv_path3,sep=',')
# Seleccion de variables
assign2025=assign2025[['userna','grade']]
# Concatenando ambos data set de assignment
assign=pd.concat([assign2024,assign2025])
# Reemplazando los valores de grade con valor -1 a 0 (-1 es no entrego)
assign['grade'] = assign['grade'].replace(-1, 0)
# Calculando el promedio de nota de actividades en los ultimos 2 periodos por userna
assign_agg=assign.groupby('userna')['grade'].mean()
# Asegurarse de que ambas columnas sean de tipo str
survey5_wider['username'] = survey5_wider['username'].astype(str)
assign_agg.index = assign_agg.index.astype(str) # Change to access the index, not a column
# Realizando el join de survey y assign
est=pd.merge(survey5_wider,assign_agg, left_on='username', right_on='userna', how='inner')
# Eliminamos las variables que ya no tienen utilidad
est.drop(columns=['id'],inplace=True,axis=1)
# Variables demograficas
vars_dem=est.columns[1:12]
# Seleccion de variables demograficas
est_dem=est[vars_dem]
# Seleccion de variables
est_clust_1=est[['username','grade',60,65,68,66,67]]
# Renombrando las variables
est_clust_1 = est_clust_1.rename(columns={60: 'semestre',
                                          65: 'situacion_laboral',
                                      68: 'relacion_amigos',
                                      66: 'grado_padre',
                                      67: 'grado_madre',
                                     })

map_semestre = {
    1: 'primero',
    2: 'segundo',
    3: 'tercero',
    4: 'cuarto',
    5: 'quinto',
    6: 'sexto',
    7: 'séptimo',
    8: 'octavo',
    9: 'noveno',
    10: 'décimo'
}
# Realizando la transformacion de las categorias para las variables categoricas
map_situacion_laboral = {
    1: 'Empleo_medio_tiempo',
    2: 'Empleo_tiempo_completo',
    3: 'Desempleado',
    4: 'Trabajo_cuenta_propia',
    5: 'Estudiante',
    6: 'Retirado',
    7: 'Sin_datos'  # si quieres añadir este nivel vacío
}
map_relacion_amigos = {
    1: 'Excelente',
    2: 'Muy_buena',
    3: 'Regular',
    4: 'Mala'
}
map_grado_padre = {
    1: 'Primaria',
    2: 'Secundaria',
    3: 'Preparatoria',
    4: 'Licenciatura',
    5: 'Posgrado',
    6: 'Doctorado',
    7: 'Sin estudios'
}
map_grado_madre = map_grado_padre.copy()

# Aplicar la transformación en tu DataFrame
est_clust_1['semestre'] = est_clust_1['semestre'].map(map_semestre)
est_clust_1['situacion_laboral'] = est_clust_1['situacion_laboral'].map(map_situacion_laboral)
est_clust_1['relacion_amigos'] = est_clust_1['relacion_amigos'].map(map_relacion_amigos)
est_clust_1['grado_padre'] = est_clust_1['grado_padre'].map(map_grado_padre)
est_clust_1['grado_madre'] = est_clust_1['grado_madre'].map(map_grado_madre)

##########
est_clust_norm1 = est_clust_1.copy()
scaler = preprocessing.MinMaxScaler()
est_clust_norm1[['grade']] = scaler.fit_transform(est_clust_norm1[['grade']])
#copia sin columna username
df_clust = est_clust_1.drop(columns=['username','semestre'])
# Asegurar que las columnas categóricas sean strings
categorical_cols = ['situacion_laboral', 'relacion_amigos', 'grado_padre', 'grado_madre']
for col in categorical_cols:
    df_clust[col] = df_clust[col].astype(str)

# Convertimos a matriz para KPrototypes
matrix = df_clust.to_numpy()
# Índices de columnas categóricas
cat_indices = [df_clust.columns.get_loc(col) for col in categorical_cols]
# K-Prototypes con 2 clusters (no más de 5 muestras)
kproto = KPrototypes(n_clusters=3, init='Cao', verbose=1)
# Fit predict
clusters = kproto.fit_predict(matrix, categorical=cat_indices)
#recuperar username y cluster
est_clust_1['cluster'] = clusters

# Mapeo de colores y orden de prioridad
CLUSTER_COLORS = {
    0: "#FFD700",  # amarillo
    1: "#28a745",  # verde
    2: "#dc3545",  # rojo
}
CLUSTER_PRIORITY = {2: 0, 0: 1, 1: 2}  # Orden deseado: rojo → amarillo → verde
STUDENTS_PER_PAGE = 10
# App Dash
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
#                                               "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"])

dash.register_page(__name__, path='/semaforoxsem', name='Semaforización')

def create_kpi(color, title, count, icon):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.I(className=f"bi {icon} kpi-icon", style={"backgroundColor": color})
                ], className="me-3"),
                html.Div([
                    html.P(title, className="mb-1 text-secondary fw-medium", style={"fontSize": "0.95rem"}),
                    html.H3(str(count), className="fw-bold mb-0", style={"fontSize": "1.9rem", "color": "#212529"})
                ])
            ], className="d-flex align-items-center")
        ]),
        className="shadow kpi-card border-0",
        style={"backgroundColor": "#ffffff", "padding": "20px", "minHeight": "120px"}
    )

def create_html_table(data, current_page=1, page_size=10):
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    page_data = data.iloc[start_idx:end_idx]

    rows = []
    for i, row in enumerate(page_data.itertuples(), start=start_idx + 1):
        color = CLUSTER_COLORS[row.cluster]
        rows.append(html.Tr([
            html.Td(
                html.Span(i, className="fw-bold text-primary"),
                className="align-middle"
            ),
            html.Td(row.username, className="align-middle"),
            html.Td(f"{row.grade:.2f}", className="align-middle"),
            html.Td(html.Div(
                style={
                    'height': '30px',
                    'width': '30px',
                    'borderRadius': '50%',
                    'backgroundColor': color,
                    'margin': 'auto',
                    'boxShadow': '0 0 5px rgba(0,0,0,0.3)',
                },
                title=f"Semestre: {row.semestre}"
            ), className="align-middle")
        ], className="table-row-animated"))

    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("#"), html.Th("Usuario"), html.Th("Nota"), html.Th("Semáforo")
        ]), className="table-light"),
        html.Tbody(rows)
    ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        className="mt-3 text-center table-rounded shadow-sm"
    )
    return table

def create_pagination_controls(total_pages, current_page):
    buttons = []

    buttons.append(
        dbc.Button("« Anterior", id={'type': 'page-nav', 'action': 'prev'}, outline=True,
                   color="secondary", disabled=(current_page == 1), className="me-2")
    )

    for i in range(1, total_pages + 1):
        buttons.append(
            dbc.Button(str(i), id={'type': 'page-item', 'index': i},
                       color="primary" if i == current_page else "light",
                       outline=(i != current_page),
                       className="me-1 mb-1")
        )

    buttons.append(
        dbc.Button("Siguiente »", id={'type': 'page-nav', 'action': 'next'}, outline=True,
                   color="secondary", disabled=(current_page == total_pages), className="ms-2")
    )

    return html.Div(
        dbc.ButtonGroup(buttons, className="flex-wrap"),
        className="d-flex justify-content-center mt-4"
    )

def get_current_page_from_children(pagination_children):
    for child in pagination_children['props']['children']:
        if isinstance(child, dict) and child.get('props', {}).get('color') == 'primary':
            try:
                return int(child['props']['children'])
            except:
                continue
    return 1

layout = dbc.Container([
    html.H2("📊 Dashboard Semáforo de Estudiantes", className="my-4 text-center fw-bold"),

    dbc.Row([
        dbc.Col(dbc.Label("Filtrar por semestre:", className="fw-bold mb-1"), width="auto"),
        dbc.Col(
            dcc.Dropdown(
                id='semestre-filter',
                options=[{'label': s, 'value': s} for s in sorted(est_clust_1['semestre'].unique())] + [{'label': 'Todos', 'value': 'Todos'}],
                value='Todos',
                clearable=False,
                className="w-100"
            ),
            md=4, xs=12
        ),
    ], className="mb-4 justify-content-center"),

    dbc.Row(id="kpi-containerr", className="mb-4 g-3"),
    html.Div(id="table-container"),
    html.Div(id="pagination-container")
], fluid=True)


@dash.callback(
    Output('kpi-containerr', 'children'),
    Output('table-container', 'children'),
    Output('pagination-container', 'children'),
    Input('semestre-filter', 'value'),
    Input({'type': 'page-item', 'index': dash.ALL}, 'n_clicks'),
    Input({'type': 'page-nav', 'action': dash.ALL}, 'n_clicks'),
    State('pagination-container', 'children'),
     prevent_initial_call=False
)
def update_dashboard(semestre, page_clicks, nav_clicks, pagination_children):
    filtered_df = est_clust_1 if semestre == 'Todos' else est_clust_1[est_clust_1['semestre'] == semestre]
    filtered_df = filtered_df.copy()
    filtered_df['priority'] = filtered_df['cluster'].map(CLUSTER_PRIORITY)
    filtered_df = filtered_df.sort_values(by='priority').reset_index(drop=True)
    filtered_df.reset_index(inplace=True)

    total_pages = math.ceil(len(filtered_df) / STUDENTS_PER_PAGE)
    current_page = 1

    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if "index" in trigger_id:
            current_page = int(eval(trigger_id)['index'])
        elif "action" in trigger_id:
            action = eval(trigger_id)['action']
            current_page = get_current_page_from_children(pagination_children)
            if action == "prev":
                current_page = max(1, current_page - 1)
            elif action == "next":
                current_page = min(total_pages, current_page + 1)

    start = (current_page - 1) * STUDENTS_PER_PAGE
    end = start + STUDENTS_PER_PAGE
    df_page = filtered_df.iloc[start:end]
    table = create_html_table(df_page)
    pagination = create_pagination_controls(total_pages, current_page)

    kpi_cards = [
        dbc.Col(create_kpi("#DC3545", "Estudiantes en Rojo", (filtered_df['cluster'] == 2).sum(), "bi-exclamation-circle-fill"), xs=12, md=4),
        dbc.Col(create_kpi("#FFC107", "Estudiantes en Amarillo", (filtered_df['cluster'] == 0).sum(), "bi-exclamation-triangle-fill"), xs=12, md=4),
        dbc.Col(create_kpi("#28A745", "Estudiantes en Verde", (filtered_df['cluster'] == 1).sum(), "bi-check-circle-fill"), xs=12, md=4),
    ]

    return kpi_cards, table, pagination
  
