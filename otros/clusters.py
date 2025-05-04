import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

# Obtener la ruta absoluta del directorio actual (es decir, 'pages')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Construir la ruta absoluta al archivo CSV dentro de 'data'
csv_path = os.path.join(BASE_DIR,  'data', '02survey.csv')
csv_path1 = os.path.join(BASE_DIR,  'data', '01 users1.csv')
csv_path2 = os.path.join(BASE_DIR,  'data', '01 assignament.csv')
csv_path3 = os.path.join(BASE_DIR,  'data', '02 assignament.csv')

# Suponiendo que tienes este DataFrame base
#cargar datos
df = pd.read_csv('data/02survey.csv',sep=',') 
#df = pd.read_csv(csv_path,sep=',')  # Tu dataset con todas las columnas mencionadas
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
#carga segundo archivo csv
df_user = pd.read_csv('data/01 users1.csv',sep=',')
#df_user = pd.read_csv(csv_path1,sep=',')
# Realizando el join entre survey y mattricula para obtener el username de cada userid
survey5_wider=pd.merge(survey4_wider, df_user[['id','username']], left_on='userid', right_on='id', how='inner')
#carga tercer archivo csv
assign2024=pd.read_csv('data/01 assignament.csv',sep=',')
#assign2024=pd.read_csv(csv_path2,sep=',')
# Seleccion de variables
assign2024=assign2024[['userna','grade']]
#carga quinto archivo csv
assign2025=pd.read_csv('data/02 assignament.csv',sep=',')
#assign2025=pd.read_csv(csv_path3,sep=',')
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
est_clust1=est[['grade',65,68,66,67]]

# Renombrando las variables
est_clust1 = est_clust1.rename(columns={65: 'situacion_laboral',
                                      68: 'relacion_amigos',
                                      66: 'grado_padre',
                                      67: 'grado_madre' 
                                     })
#Mapear datos usando diccionarios
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

est_clust1['situacion_laboral'] = est_clust1['situacion_laboral'].map(map_situacion_laboral)
est_clust1['relacion_amigos'] = est_clust1['relacion_amigos'].map(map_relacion_amigos)
est_clust1['grado_padre'] = est_clust1['grado_padre'].map(map_grado_padre)
est_clust1['grado_madre'] = est_clust1['grado_madre'].map(map_grado_madre)


# Inicializar app Dash
#dash.register_page(__name__, path='/clusters', name='Clusters')
#creacion de clusters
from sklearn import preprocessing
est_clust_norm = est_clust1.copy()
scaler = preprocessing.MinMaxScaler()
est_clust_norm[['grade']] = scaler.fit_transform(est_clust_norm[['grade']])
from kmodes.kprototypes import KPrototypes
kproto = KPrototypes(n_clusters=3, init='Cao')
clusters = kproto.fit_predict(est_clust_norm, categorical=[1,2,3,4])
#parametro categorical definimos los indices de las variables categoricas
#join data with labels
labels = pd.DataFrame(clusters)
labeledStud = pd.concat((est_clust1,labels),axis=1)
labeledStud = labeledStud.rename({0:'labels'},axis=1)
# Agrupando los datos por cluster y calculando la media de cada variable
categorical_vars = ['situacion_laboral', 'relacion_amigos', 'grado_padre', 'grado_madre']

# Inicializa Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout del dashboard
app.layout = dbc.Container([
    html.H2("Distribución de variables categóricas por Clúster", className="my-4 text-center"),

    dbc.Row([
        dbc.Col([
            html.Label("Selecciona variable categórica:"),
            dcc.Dropdown(
                id='categoria-dropdown',
                options=[{'label': var.replace("_", " ").capitalize(), 'value': var} for var in categorical_vars],
                value='situacion_laboral',
                clearable=False
            )
        ], width=6)
    ], className="mb-4"),

    dcc.Graph(id='grafico-categorico')
], fluid=True)


# Callback
@app.callback(
    Output('grafico-categorico', 'figure'),
    Input('categoria-dropdown', 'value')
)
def actualizar_grafico(variable):
    # Tabla de conteo por cluster y categoría
    count_data = labeledStud.groupby(['labels', variable]).size().reset_index(name='count')

    # Total por cluster para porcentajes
    total_per_cluster = labeledStud.groupby('labels').size().to_dict()

    # Agregar porcentaje
    count_data['pct'] = count_data.apply(
        lambda row: 100 * row['count'] / total_per_cluster[row['labels']], axis=1
    )

    # Gráfico de barras
    fig = px.bar(
        count_data,
        x='labels',
        y='count',
        color=variable,
        text=count_data['pct'].apply(lambda x: f'{x:.1f}%'),
        barmode='group',
        labels={'labels': 'Cluster', 'count': 'Cantidad'},
        title=f'Distribución de {variable.replace("_", " ")} por Clúster',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(legend_title_text=variable.replace("_", " ").capitalize())

    return fig


# Ejecutar el servidor
if __name__ == '__main__':
    app.run_server(debug=True)