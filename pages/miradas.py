#importar librerias
import  dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd




dash.register_page(__name__,path="/miradas")

#cargar datos
#https://raw.githubusercontent.com/angelus0786/educational_data/refs/heads/main/01survey.csv
try:
    df = pd.read_csv("01survey.csv",sep=',')
except Exception as e:
    print(f"Error al cargar el archivo: {e}")



df_mark1 = df.copy() #no olvidar homologacion
df_mark1.item = df_mark1.item.replace([81,82,83,84,85,86,87,88,89,90,91],[59,60,61,62,63,64,65,66,67,68,69])
df_mark1.item = df_mark1.item.replace([48,49,50,51,52,53,54,55,56,57,58],[59,60,61,62,63,64,65,66,67,68,69])
df_mark2 = df_mark1.copy()

##Mirada1 Edad vs Estado civil
#identificar edades
df_m1 = df_mark1.copy()
#print("clolumnas df_m1",df_m1.columns)
mark1 = df_m1['item'].isin([63])
df_m1.value = df_m1.value.replace([1,2,3,4,5,6],['18 to 20 years','21 to 22 years','23 to 25 years','26 to 28 years','29 to 30 years','over 31'])
df_m1.rename(columns={'value':'Age','course':'Course'}, inplace=True)

#identificar marital status
df_m2 = df_mark2.copy()
mark2 = df_m2['item'].isin([64])
df_m2.value = df_m2.value.replace([1,2,3,4], ['Single', 'Married', 'Divorced', 'Widowed'])
df_m2.rename(columns={'value':'Marital Status','course':'Course'}, inplace=True)

##unit tablas
df_merge1 = pd.merge(df_m1[mark1],df_m2[mark2], left_on='userId', right_on='userId')
#graficar Edad y estado civl
df_merge1 = df_merge1.groupby(['Age','Marital Status'])['userId'].count().reset_index(name='Number of Students')

#Mirada 2
#identificar registros Maximo estudio de padre
df_mark3 = df_mark1.copy()
df_m3 = df_mark3.copy()
mark3 = df_m3['item'].isin([66])
df_m3.value = df_m3.value.replace([1,2,3,4,5,6,7], ['Elementary school','Middle school','High School','Bachelor\'s degree','Master\'s degree','Doctorate','No studies'])
df_m3.rename(columns={'value':'Maximum Degree of Father','course':'Course'}, inplace=True)
#print("mark3: ",mark3)

#identificar registros de pareja
df_mark4 = df_mark1.copy()
df_m4 = df_mark4.copy()
mark4 = df_m4['item'].isin([69])
df_m4.value = df_m4.value.replace([1,2], ['Yes', 'NO'])
df_m4.rename(columns={'value':'partner','course':'Course'}, inplace=True)

df_merge2 = pd.merge(df_m3[mark3],df_m4[mark4], left_on='userId', right_on='userId')
df_merge2 = df_merge2.groupby(['Maximum Degree of Father', 'partner'])['userId'].count().reset_index(name='Number of Students')
color_map = {
    'Yes':'#1f77b4',  # Azul
    'No':'#d62728'   # Rojo
    }

## Mirada 3
#identificar registros de situacion laboral
df_mark5 = df_mark1.copy()
df_m5 = df_mark5.copy()
mark5 = df_m5['item'].isin([65])
df_m5.value = df_m5.value.replace([1,2,3,4,5,6],['Part-time', 'Full-time', 'Unemployed', 'Self-employed', 'Student', 'Retired'])
df_m5.rename(columns={'value':'Employment Status','course':'Course'}, inplace=True)
#unir tablas
df_merge3 = pd.merge(df_m5[mark5],df_m4[mark4], left_on='userId', right_on='userId')
df_merge3 = df_merge3.groupby(['Employment Status', 'partner'])['userId'].count().reset_index(name='Number of Students')
color_map2 = {
   'Yes':'#ff7f0e',  # Naranja
    'No':'#2ca02c'   # Verde
    }
color_map3 = {
   'Yes':'#ff7f0e',  # Naranja
    'No':'#2ca02c'   # Verde
    }
# Mirada 4
#identificar registros de madre
df_mark6 = df_mark1.copy()
df_m6 = df_mark6.copy()
mark6 = df_m6['item'].isin([67])
df_m6.value = df_m6.value.replace([1,2,3,4,5,6,7], ['Elementary school','Middle school','High School',
                                                    'Bachelor\'s degree','Master degree','Doctorate','No studies'])
df_m6.rename(columns={'value':'Maximum Degree of Mother','course':'Course'}, inplace=True)
#unir tablas
df_merge4 = pd.merge(df_m3[mark3],df_m6[mark6], left_on='userId', right_on='userId')
#graficar
df_merge4 = df_merge4.groupby(['Maximum Degree of Father', 'Maximum Degree of Mother'])['userId'].count().reset_index(name='Number of Students')



#Objetos plotly.graph
data1 = []
for status in df_merge1['Marital Status'].unique():
    df_filtered = df_merge1[df_merge1['Marital Status'] == status]
    data1.append(go.Bar(
        x=df_filtered['Age'],
        y=df_filtered['Number of Students'],
        name=status
    ))  

layout1 = go.Layout(
    title='1: Distribution of Students\nby Age vs Marital Status',
    xaxis_title='Age',
    yaxis_title='Number of Students',
    legend_title='Marital Status',
     barmode='group' 
)

data2 = []
for status in df_merge2['partner'].unique():
    df_filtered = df_merge2[df_merge2['partner'] == status]
    data2.append(go.Bar(
        x=df_filtered['Maximum Degree of Father'],
        y=df_filtered['Number of Students'],
        name=f'Partner: {status}',
        marker=dict(color=color_map.get(status, 'green'))
    ))  

layout2 = go.Layout(
    title='2: Distribution of Students\nby Maximum Degree of Father vs  Partner',
    xaxis_title='Maximum Degree of Father',
    yaxis_title='Number of Students',
    legend_title='partner',
    barmode='stack',
    template="plotly_white"
)

data3 = []
for emp_status in df_merge3['partner'].unique():
    df_filtered3 = df_merge3[df_merge3['partner'] == emp_status]
    data3.append(go.Bar(
        x=df_filtered3['Employment Status'],
        y=df_filtered3['Number of Students'],
        name=f'Partner: {emp_status}',
        marker=dict(color=color_map3.get(emp_status, 'red'))
    ))  

layout3 = go.Layout(
    title='3:Distribution of Students\nby Employment Status vs Partner',
    xaxis_title='Employment Status',
    yaxis_title='Number of Students',
    legend_title='partner',
    barmode='group',
    template="plotly_white"
    #color_map = colores_map
)
data4 = []
for MDMother_status in df_merge4['Maximum Degree of Mother'].unique():
    df_filtered4 = df_merge4[df_merge4['Maximum Degree of Mother'] == MDMother_status]
    data4.append(go.Bar(
        x=df_filtered4['Maximum Degree of Father'],
        y=df_filtered4['Number of Students'],
        name=f'MDM:{MDMother_status}'#,
        #marker=dict(color=color_map.get(MDMother_status, 'red'))
    ))  

layout4 = go.Layout(
    title='4: Distribution of Students\nby Maximum Study of Father vs Maximum Study of Mother',
    xaxis_title='Maximum Degree of Father',
    yaxis_title='Number of Students',
    legend_title='Maximum Degree of Mother',
    barmode='group',
    template="plotly_white"
    #color_map = colores_map
)

#definicion del Layout de la app a partir de componentes HTML y Core
layout = dbc.Container([
        html.H1('Miradas hacia los estudiantes\n Instituto Tecnológico Superior de Perote',),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='bar-chart',
                    figure={'data':data1,'layout':layout1}
                )
            ], width=6),
            dbc.Col([
                dcc.Graph(
                    id='bar-chart2',
                    figure={'data':data2,'layout':layout2}
                )
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='bar-chart3',
                    figure={'data':data3,'layout':layout3}
                )
            ], width=6),
            dbc.Col([
                dcc.Graph(
                    id='bar-chart4',
                    figure={'data':data4,'layout':layout4}
                )
            ], width=6)
        ])
],
                       fluid=True, 
                       className="container-fluid"             )


#Sentencias para abrir el servidor al ejecutar este script
#if __name__=='__main__':
 #   app.run_server()