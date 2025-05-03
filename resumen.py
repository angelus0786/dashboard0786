import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import seaborn as sns
import pandas as pd

# Suponiendo que tienes este DataFrame base
df = pd.read_csv('data/02survey.csv')  # Tu dataset con todas las columnas mencionadas
#eliminar columnas no relevantes
df = df.drop(['idItem','idFeedback','completed'], axis=1)
# Seleccion de variables utiles y pasando las variables a minuscula
survey_2=df[['userId','item','value','period']]
survey_2.columns=survey_2.columns.str.lower()
# Seleccion de estudiantes finales a partir de 5* y 6* ciclo
estudiantes=survey_2[(survey_2['item']==60) & (survey_2['value'].isin([1,2,3,4,5,6])) ]['userid']
survey_3=survey_2[survey_2['userid'].isin(estudiantes)]
# Obtener el índice del mayor valor de 'periodo' por 'userid item' (por que no usar ambos periodos?)
idx = survey_2.groupby(['userid','item'])['period'].idxmax()
# Filtrar el DataFrame usando esos índices
survey_3 = survey_2.loc[idx].reset_index(drop=True)
# Eliminando la variable period
survey_3.drop('period',axis=1,inplace=True)
# Reestructurando el data set
survey4_wider = survey_3.pivot(index='userid', columns='item', values='value').reset_index()
survey4_wider.columns.name = None
# Por ultimo la encuesta se realizo a modalidad mixta
survey4_wider[62]=2
df_user = pd.read_csv("data/01 users1.csv",sep=',')
# Realizando el join entre survey y mattricula para obtener el username de cada userid
survey5_wider=pd.merge(survey4_wider, df_user[['id','username']], left_on='userid', right_on='id', how='inner')
assign2024=pd.read_csv("data/01 assignament.csv")
# Seleccion de variables
assign2024=assign2024[['userna','grade']]
assign2025=pd.read_csv("data/02 assignament.csv")
# Seleccion de variables
assign2025=assign2025[['userna','grade']]
# Concatenando ambos data set de assignment
assign=pd.concat([assign2024,assign2025])
# Reemplazando los valores de grade con valor -1 a 0
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
vars_dem=est.columns[1:13]
# Seleccion de variables demograficas
est_dem=est[vars_dem]
# Seleccion de variables
est_clust1=est[['grade',62,63,64,65,68,66,67,69,'username']]

# Renombrando las variables
est_clust1 = est_clust1.rename(columns={62:'modalidad',
                                      63: 'edad',
                                      64: 'estado_civil',
                                      65: 'situacion_laboral',
                                      68: 'relacion_amigos',
                                      66: 'grado_padre',
                                      67: 'grado_madre',
                                      69: 'tiene_pareja',  
                                      'username':'matricula'  
                                     })
#Mapear datos usando diccionarios
# Realizando la transformacion de las categorias para las variables categoricas
map_modalidad = {
    1: 'Presencial',    
    2: 'Mixta'
    }
map_edad = {
    1: '18-20 años',
    2: '21-22 años',
    3: '23-25 años',
    4: '26-28 años',
    5: '29-30 años',
    6: 'Más de 31'
}
map_estado_civil = {
    1: 'Soltero',
    2: 'Casado',
    3: 'Divorciado',
    4: 'Viudo'
}
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

map_tiene_pareja = {
    1: 'Si',
    2: 'No'
}

# Aplicar la transformación en tu DataFrame
est_clust1['modalidad'] = est_clust1['modalidad'].map(map_modalidad)
est_clust1['edad'] = est_clust1['edad'].map(map_edad)
est_clust1['estado_civil'] = est_clust1['estado_civil'].map(map_estado_civil)
est_clust1['situacion_laboral'] = est_clust1['situacion_laboral'].map(map_situacion_laboral)
est_clust1['relacion_amigos'] = est_clust1['relacion_amigos'].map(map_relacion_amigos)
est_clust1['grado_padre'] = est_clust1['grado_padre'].map(map_grado_padre)
est_clust1['grado_madre'] = est_clust1['grado_madre'].map(map_grado_madre)
est_clust1['tiene_pareja'] = est_clust1['tiene_pareja'].map(map_tiene_pareja)


# Inicializar app Dash
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Resumen del Estudiante"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Análisis Individual de Estudiantes",
                        className='text-center text-primary mb-4'), width=12)
    ]),
 dbc.Row([
        dbc.Col([
            dbc.Label("Ingrese Matrícula del Estudiante:"),
            dbc.Input(id='input-matricula', type='text', placeholder='Ej. 22050003', debounce=True)
        ], width=4)
    ], className='mb-4'),
     dbc.Row(id='kpi-container', className="mb-4 g-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-edad-estado'), width=6),
        dbc.Col(dcc.Graph(id='grafico-grado-pareja'), width=6),
    ], className='mb-4'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico-laboral-pareja'), width=6),
        dbc.Col(dcc.Graph(id='grafico-amigos-modalidad'), width=6),
    ])
], fluid=True)

# Callbacks
@app.callback(
    [Output('grafico-edad-estado', 'figure'),
     Output('grafico-grado-pareja', 'figure'),
     Output('grafico-laboral-pareja', 'figure'),
     Output('grafico-amigos-modalidad', 'figure'),
     Output('kpi-container', 'children')],
    Input('input-matricula', 'value')
)
def actualizar_dashboard(matricula):
    # Validar entrada vacía o matrícula inexistente
     # Si la matrícula está vacía, mostrar los gráficos con todos los datos
    if not matricula:
       # Agrupaciones globales
        fig1 = px.bar(est_clust1.groupby(['edad', 'estado_civil'])['matricula'].count().reset_index(name='Total'),
                      x='edad', y='Total', color='estado_civil',
                      title='Edad vs Estado Civil (Todos los estudiantes)')

        fig2 = px.bar(est_clust1.groupby(['grado_padre', 'situacion_laboral'])['matricula'].count().reset_index(name='Total'),
                      x='grado_padre', y='Total', color='situacion_laboral',
                      title='Grado del padre vs Situación laboral (Todos los estudiantes)')

        fig3 = px.bar(est_clust1.groupby(['relacion_amigos', 'estado_civil'])['matricula'].count().reset_index(name='Total'),
                      x='relacion_amigos', y='Total', color='estado_civil',
                      title='Relación con amigos vs Estado civil (Todos los estudiantes)')
        
        fig4 = px.bar(est_clust1.groupby(['modalidad', 'tiene_pareja'])['matricula'].count().reset_index(name='Total'),
                      x='modalidad', y='Total', color='tiene_pareja',
                      title='Modalidad vs Tiene Pareja (Todos los estudiantes)')

        kpi_text = html.Div("Mostrando datos globales", style={'color': 'green', 'fontWeight': 'bold'})
        return fig1, fig2, fig3, fig4, kpi_text 
      
     # Validación si la matrícula existe en el DataFrame
    if 'matricula' not in est_clust1.columns or not est_clust1['matricula'].astype(str).isin([str(matricula)]).any():
        mensaje_error = html.Div("⚠️ Matrícula no encontrada o vacía", style={'color': 'red', 'fontWeight': 'bold'})
        placeholder = px.bar(title="Sin datos")
        return placeholder, placeholder, placeholder, mensaje_error

    # Filtro por matrícula
    estudiante = est_clust1[est_clust1['matricula'].astype(str) == str(matricula)].iloc[0]
    
    # Crear gráficas personalizadas
    # Gráficos por variable con Plotly
    fig1 = px.bar(est_clust1.groupby(['edad', 'estado_civil'])['matricula'].count().reset_index(name='Cantidad'),
                  x='edad', y='Cantidad', color='estado_civil',
                  title="Edad vs Estado Civil")
    fig1.add_vline(x=estudiante['edad'], line_dash="dot", line_color="red")

    fig2 = px.bar(est_clust1.groupby(['grado_padre', 'situacion_laboral'])['matricula'].count().reset_index(name='Cantidad'),
                  x='grado_padre', y='Cantidad', color='situacion_laboral',
                  title="Grado del Padre vs Situación Laboral")
    fig2.add_vline(x=estudiante['grado_padre'], line_dash="dot", line_color="red")

    fig3 = px.bar(est_clust1.groupby(['situacion_laboral', 'estado_civil'])['matricula'].count().reset_index(name='Cantidad'),
                  x='situacion_laboral', y='Cantidad', color='estado_civil',
                  title="Situación Laboral vs Estado Civil")
    fig3.add_vline(x=estudiante['situacion_laboral'], line_dash="dot", line_color="red")

    fig4 = px.bar(est_clust1.groupby(['relacion_amigos', 'modalidad'])['matricula'].count().reset_index(name='Cantidad'),
                  x='relacion_amigos', y='Cantidad', color='modalidad',
                  title="Relación con Amigos vs Modalidad")
    fig4.add_vline(x=estudiante['relacion_amigos'], line_dash="dot", line_color="red")
    
    # KPI Cards
    kpi_cards = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Calificación", className="card-title"),
                html.P(f"{estudiante['grade']:.2f}", className="card-text")
            ])
        ], color="info", inverse=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Edad", className="card-title"),
                html.P(estudiante['edad'], className="card-text")
            ])
        ], color="primary", inverse=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Estado Civil", className="card-title"),
                html.P(estudiante['estado_civil'], className="card-text")
            ])
        ], color="secondary", inverse=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Situación Laboral", className="card-title"),
                html.P(estudiante['situacion_laboral'], className="card-text")
            ])
        ], color="dark", inverse=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Modalidad", className="card-title"),
                html.P(estudiante['modalidad'], className="card-text")
            ])
        ], color="success", inverse=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Relación con Amigos", className="card-title"),
                html.P(estudiante['relacion_amigos'], className="card-text")
            ])
        ], color="warning", inverse=True), width=2),
    ])

    return fig1, fig2, fig3, fig4, kpi_cards
    
# Ejecutar app
if __name__ == '__main__':
    app.run_server(debug=True)