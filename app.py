import dash
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
from dash import dcc, html
from flask import Flask

df = pd.read_csv('ventas.csv')

external_stylesheets = [
    {
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3',
        'crossorigin': 'anonymous'
    },
    ]

external_scripts = [
    {
        'src': 'https://code.jquery.com/jquery-3.6.0.min.js',
        'integrity': 'sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=',
        'crossorigin': 'anonymous'
    },
    {
        'src': 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
        'integrity': 'sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p',
        'crossorigin': 'anonymous'
    },
    ]

server = Flask(__name__)

if __name__ == ('__main__'):
    app = dash.Dash(__name__,
                    external_stylesheets=external_stylesheets,
                    external_scripts=external_scripts,
                    server=server,
                    title="Daschboard - Ventas")
else:
    app = dash.Dash(__name__,
                    external_stylesheets=external_stylesheets,
                    external_scripts=external_scripts,
                    server=server,
                    requests_pathname_prefix='/dashboard-ventas/',
                    title="Daschboard - Ventas")

app.layout = html.Div([
    html.H1("Dashboard de Compras", className="text-center"),
    html.P("Distribuidora del Valle S.A. de C.V.",className="text-center lead"),
    html.Div([
        html.Div([
            html.Label('Vendedor: ', className="form-label", htmlFor="vendedor"),
            dcc.Dropdown(
                options=list(df['Vendedor'].unique()),
                id='vendedor', clearable=True, multi=True, className='text-secondary'),
        ], className='col-sm-3'),
        html.Div([
            html.Label('Categoría: ', className="form-label", htmlFor="categoria"),
            dcc.Dropdown(
                options=list(df['Categoría'].unique()),
                id='categoria', clearable=True, multi=True),
        ], className='col-sm-3'),
        html.Div([
            html.Label('Región: ', className="form-label", htmlFor="region"),
            dcc.Dropdown(
                options=list(df['Region'].unique()),
                id='region', clearable=True, multi=True),
        ], className='col-sm-3'),
        html.Div([
            html.Label('Colorear por: ', className="form-label", htmlFor="color"),
            dcc.Dropdown(
                options=['Vendedor', 'Categoría', 'Region'],
                id='color', clearable=True, multi=False),
        ], className='col-sm-3'),
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id='gVentasMensuales', figure={}),
        ], className="col-sm-12"),
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Graph(id='gVentasVendedor', figure={}),
        ], className="col-sm-3"),
        html.Div([
            dcc.Graph(id='gVentasCategoria', figure={}),
        ], className="col-sm-3"),
        html.Div([
            dcc.Graph(id='gVentasEstado', figure={}),
        ], className="col-sm-3"),
        html.Div([
            dcc.Graph(id='gVentasPromedioVenta', figure={}),
        ], className="col-sm-3"),
    ], className="row"),
], className="bg-light text-dark", style={'padding': '20px'})

@app.callback(
    Output('gVentasMensuales', component_property='figure'),
    Output('gVentasVendedor', component_property='figure'),
    Output('gVentasCategoria', component_property='figure'),
    Input('vendedor', component_property='value'),
    Input('categoria', component_property='value'),
    Input('region', component_property='value'),
    Input('color', component_property='value'))
def updateGraphVentasMensuales(vendedor, categoria, region, color):
    dfg = filtraDF(df.copy(), vendedor, categoria, region)
    if color is None:
        figVM = px.histogram(
            dfg, x='Fecha de orden', y='Ingresos', nbins=12,
            title="Ventas Totales por Mes", text_auto=True)
        figVV = px.histogram(
            dfg, y='Vendedor', x='Ingresos',
            title="Ventas por Vendedor", text_auto=True)
        figVC = px.histogram(
            dfg, y='Categoría', x='Ingresos',
            title="Ventas por Categoria de Producto", text_auto=True)
    else:
        figVM = px.histogram(
            dfg, x='Fecha de orden', y='Ingresos', nbins=12,
            title="Ventas Totales por Mes", text_auto=True, color=color)
        figVV = px.histogram(
            dfg, y='Vendedor', x='Ingresos',
            title="Ventas por Vendedor", text_auto=True, color=color)
        figVC = px.histogram(
            dfg, y='Categoría', x='Ingresos',
            title="Ventas por Categoria de Producto", text_auto=True, color=color)
    figVM.update_layout(bargap=0.2)
    return figVM, figVV, figVC

@app.callback(
    Output('gVentasEstado', component_property='figure'),
    Output('gVentasPromedioVenta', component_property='figure'),
    Input('vendedor', component_property='value'),
    Input('categoria', component_property='value'),
    Input('region', component_property='value'))
def updateGraphVentasEstado(vendedor, categoria, region):
    dfg = filtraDF(df.copy(), vendedor, categoria, region)
    gjson = json.load(open('mexicoHigh.json', 'r'))
    figVE = px.choropleth(
        dfg, geojson=gjson, title='Ventas por Estado',
        locations='Estado', featureidkey='properties.name',
        color='Ingresos', color_continuous_scale='blues',
        )
    figVE.update_geos(
        showcountries=True, showcoastlines=True,
        showland=True, fitbounds='locations')
    counts, bins = np.histogram(
        dfg.dropna(subset=['Ingresos'])['Ingresos'], bins=5)
    data = [
        {'cantidad': cant, 'rango': f'${bins[idx]:,.0f} - ${bins[idx + 1]:,.0f}'}
        for idx, cant in enumerate(counts)]
    figPV = px.pie(
        data, values='cantidad', names='rango',
        hole=0.4, title="Promedio de Venta")
    return figVE, figPV

def filtraDF(dfg, vendedor, categoria, region):
    if vendedor is not None and len(vendedor) > 0:
        dfg = dfg[dfg['Vendedor'].isin(vendedor)]
    if categoria is not None and len(categoria) > 0:
        dfg = dfg[dfg['Categoría'].isin(categoria)]
    if region is not None and len(region) > 0:
        dfg = dfg[dfg['Region'].isin(region)]
    return dfg

if __name__ == ('__main__'):
    app.run(debug=True, port=8055)
