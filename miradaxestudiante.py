import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np  
from scipy.stats import chi2_contingency
import plotly.graph_objects as go
import matplotlib.pyplot as plt
#%matplotlib inline
import warnings
warnings.filterwarnings('ignore')


# Cargar el dataset
df_survey =pd.read_csv('data/02survey.csv',sep=',')  
# Relacion de cantidad de estudiantes por semestres (ciclo)
df_survey[df_survey['item']==60]['value'].value_counts()
# Seleccion de variables utiles y pasando las variables a minuscula
survey_2=df_survey[['userId','item','value','period']]
survey_2.columns=survey_2.columns.str.lower()
# Seleccion de estudiantes finales a partir de 1*,2*,3*,4*, 5* y 6* Semestre(ciclo)
estudiantes=survey_2[(survey_2['item']==60) & (survey_2['value'].isin([1,2,3,4,5,6])) ]['userid']
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
mat=pd.read_csv('data/01 users1.csv',sep=',')
# Realizando el join entre survey y mattricula para obtener el username de cada userid
survey5_wider=pd.merge(survey4_wider, mat[['id','username']], left_on='userid', right_on='id', how='inner')
assign2024=pd.read_csv('data/01 assignament.csv',sep=',')
# Seleccion de variables
assign2024=assign2024[['userna','grade']]
assign2025=pd.read_csv('data/02 assignament.csv',sep=',')
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
# Renombrando las variables
est_cor = est.rename(columns={60:'semestre',
                          61:'genero',
                          63:'edad',
                          64:'estado_civil',
                          65:'situacion_laboral',
                          68:'relacion_amigos',
                          66:'grado_padre',
                          67:'grado_madre',
                          69:'tener_pareja'
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
map_genero = {
    1: 'Masculino',
    2: 'Femenino',
    3: 'Otro'
}
map_edad = {
    1: '18-20',
    2: '21-22',
    3: '23-25',
    4: '26-28',
    5: '29-30',
    6: 'Más de 30'}
map_estado_civil = {
    1: 'Soltero',
    2: 'Casado',
    3: 'Divorciado',
    4: 'Viudo'
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
map_tener_pareja = {
    1: 'Si',
    2: 'No'
}
map_grado_madre = map_grado_padre.copy()

# Aplicar la transformación en tu DataFrame
est_cor['semestre'] = est_cor['semestre'].map(map_semestre)
est_cor['genero'] = est_cor['genero'].map(map_genero)
est_cor['edad'] = est_cor['edad'].map(map_edad)
est_cor['estado_civil'] = est_cor['estado_civil'].map(map_estado_civil)
est_cor['situacion_laboral'] = est_cor['situacion_laboral'].map(map_situacion_laboral)
est_cor['relacion_amigos'] = est_cor['relacion_amigos'].map(map_relacion_amigos)
est_cor['grado_padre'] = est_cor['grado_padre'].map(map_grado_padre)
est_cor['grado_madre'] = est_cor['grado_madre'].map(map_grado_madre)
est_cor['tener_pareja'] = est_cor['tener_pareja'].map(map_tener_pareja)

#seleccion de variables demograficas
vars_dem1=est_cor[['semestre','genero','edad','estado_civil','situacion_laboral','relacion_amigos','grado_padre','grado_madre','tener_pareja','username','grade']]
est_cor_dem = est_cor[vars_dem1.columns]
# Convertir todas las columnas a tipo objeto (por seguridad)
df_est_cor = est_cor_dem.astype(str)
# Filtrar solo columnas categóricas
categorical_df = df_est_cor.select_dtypes(include='object')

#inicializar la app
app = dash.Dash(__name__,
          external_stylesheets=[dbc.themes.BOOTSTRAP],
          suppress_callback_exceptions=True
          )

# Layout con filtros y tarjetas
app.layout = dbc.Container([
    html.H2("Análisis de asociaciones entre variables", className='text-center text-primary mb-4'),
    dbc.Row([
       dbc.Col([
            dbc.Label("Ingrese Matrícula del Estudiante:"),
            dbc.Input(id='filtro_username', type='text', placeholder='Ej. 22050003') #, debounce=True
        ], md=4),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='filtro_genero',
                options=[{'label': i, 'value': i} for i in sorted(categorical_df['genero'].dropna().unique())],
                placeholder="Filtrar por género",
                multi=True,
                value=[]        
            ),
        ], md=4),

        dbc.Col([
            dcc.Dropdown(
                id='filtro_semestre',
                options=[{'label': i, 'value': i} for i in sorted(categorical_df['semestre'].dropna().unique())],
                placeholder="Filtrar por semestre",
                multi=True,
                value=[]
            ),
        ], md=4)
    ]),
     # KPIs ocultos inicialmente
    dbc.Row(id='kpi_cards', style={'display': 'none'}, className="my-4"),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Edad vs Situación Laboral"),
            dbc.CardBody(
                dcc.Graph(id='grafico_edad_sitlab'))
                         
        ]), md=6),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Situación Laboral vs Estado Civil"),
            dbc.CardBody(
                dcc.Graph(id='grafico_sitlab_edocivil'))
                
        ]), md=6),
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Situación Laboral vs Relación con Amigos"),
            dbc.CardBody(
                dcc.Graph(id='grafico_sitlab_amigos'))
        ]), md=6),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Grado de Estudio: Padre vs Madre"),
            dbc.CardBody(
                dcc.Graph(id='grafico_padre_madre'))
        ]), md=6),
    ])
], fluid=True)

def generar_graficos_vacios(mensaje):
 # Crear gráficos vacíos con título
        empty_df = pd.DataFrame(columns=['estado_civil', 'situacion_laboral', 'conteo'])
        df_vacio = pd.DataFrame(columns=['x', 'y', 'z'])  # columnas genéricas según uso
        
        fig1 = px.histogram(x=[])
        fig1.update_layout(title=mensaje)

        fig2 = px.density_heatmap(empty_df, x='estado_civil', y='situacion_laboral', z='conteo')
        fig2.update_layout(title=mensaje)

        fig3 = px.violin(df_vacio,x='x', y='y',title=mensaje)
        #fig3.update_layout(title=mensaje)

        fig4 = px.scatter(df_vacio,x='x', y='y',title=mensaje)
        #fig4.update_layout(title=mensaje)

        # Mensaje de alerta como único KPI
        alerta = dbc.Alert(mensaje, color="danger", dismissable=True, className="w-100 text-center")
        return fig1, fig2, fig3, fig4, [dbc.Col(alerta)], {'display': 'flex'}


# Callback para actualizar todos los gráficos según filtros
@dash.callback(
    Output('grafico_edad_sitlab', 'figure'),
    Output('grafico_sitlab_edocivil', 'figure'),
    Output('grafico_sitlab_amigos', 'figure'),
    Output('grafico_padre_madre', 'figure'),
    Output('kpi_cards', 'children'),
    Output('kpi_cards', 'style'),
    Input('filtro_genero', 'value'),
    Input('filtro_semestre', 'value'),
    Input('filtro_username', 'value')
)

def actualizar_graficos(genero,semestre,username):
    dff = categorical_df.copy()
   # if carrera:
    #    dff = dff[dff['carrera'] == carrera]
    if genero:
        dff = dff[dff['genero'].isin(genero)]
    if semestre:
        dff = dff[dff['semestre'].isin(semestre)]
   
    fig1 = px.histogram(dff, x="edad", color="situacion_laboral", barmode="stack",
                        title="Edad vs Situación Laboral")
    
    tabla = pd.crosstab(dff['situacion_laboral'], dff['estado_civil'])
    tabla = tabla.reset_index().melt(id_vars='situacion_laboral', var_name='estado_civil', value_name='conteo')
    fig2 = px.density_heatmap(tabla, x='estado_civil', y='situacion_laboral', z='conteo',
                               title="Situación Laboral vs Estado Civil",
                               labels={"estado_civil": "Estado Civil", "situacion_laboral": "Situación Laboral"})

    fig3 = px.violin(dff, x="situacion_laboral", y="relacion_amigos", box=True, points="all",
                     title="Situación Laboral vs Relación con Amigos",
                     labels={"situacion_laboral": "Situación Laboral", "relacion_amigos": "Relación con Amigos"})

    fig4 = px.scatter(dff, x="grado_padre", y="grado_madre",
                      title="Grado de Estudio: Padre vs Madre")
    
   
 # Añadir marcadores para el estudiante seleccionado
    if username:
        estudiante_df = dff[dff['username'] == username]
        if not estudiante_df.empty:
            estudiante = estudiante_df.iloc[0]
            # Marcas en los gráficos
            # Edad vs Situación Laboral
            fig1.add_vline(x=estudiante['edad'], line_dash="dash", line_color="black")
           
            fig2.add_trace(go.Scatter(
                x=[estudiante['estado_civil']],
                y=[estudiante['situacion_laboral']],
                mode='markers+text',
                marker=dict(color='black', size=10, symbol='x'),
                text=["Est."],
                textposition='top center',
                name='Estudiante'
            ))
           
           
            # Situación Laboral vs Relación con Amigos
            fig3.add_trace(px.scatter(x=[estudiante['situacion_laboral']], y=[estudiante['relacion_amigos']],
                                  labels={"x": "Situación Laboral", "y": "Relación con Amigos"},
                                  opacity=1.0, color_discrete_sequence=["black"]).data[0])
            # Grado de Estudio
            fig4.add_trace(px.scatter(x=[estudiante['grado_padre']], y=[estudiante['grado_madre']],
                                  opacity=1.0, color_discrete_sequence=["black"]).data[0])
            calificacion = round(float(estudiante['grade']), 2)if pd.notna(estudiante['grade']) else "N/A"
            kpi_cards = [
            dbc.Col(dbc.Card([dbc.CardHeader("Calificación"), dbc.CardBody(html.H4(calificacion))]), md=3),
            dbc.Col(dbc.Card([dbc.CardHeader("Edad"), dbc.CardBody(html.H4(estudiante['edad']))]), md=3),
            dbc.Col(dbc.Card([dbc.CardHeader("Estado Civil"), dbc.CardBody(html.H4(estudiante['estado_civil']))]), md=3),
            dbc.Col(dbc.Card([dbc.CardHeader("Relación con Amigos"), dbc.CardBody(html.H4(estudiante['relacion_amigos']))]), md=3)
            ]
            return fig1, fig2, fig3, fig4, kpi_cards, {'display': 'flex'}
        else:
         return generar_graficos_vacios("⚠️ Matrícula no encontrada. Verifique e intente nuevamente.")
    else:
        return fig1, fig2, fig3, fig4, [], {'display': 'none'}       
   
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)   
