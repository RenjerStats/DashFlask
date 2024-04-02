import dash
from dash import Input, Output
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px

def init_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/dash/",
        external_stylesheets=["https://fonts.googleapis.com/css?family=Lato"],
    )
    df = pd.date_range(0, 100, 5)

    dash_app.index_string = open("MyCode/templates/dash.html", encoding='UTF-8').read()
    dash_app.layout = get_layout(df)
        
    init_callbacks(dash_app)
    return dash_app.server


def get_layout(df):
    droplist = dcc.Dropdown(
        [1, 2, 3, 4, 5],
        value=[1, 5],
        id = 'dropdown',
        multi=True,
        clearable=False,
        optionHeight=50)
        
    layout = html.Div(
        children=[
            dcc.Graph(id="base_graph", figure=px.scatter(df)),
            droplist
        ]
    )
    return layout

def init_callbacks(app):
    @app.callback(
        Output('base_graph', 'figure'),
        Input('dropdown', 'value'),
        prevent_initial_call=True)
    def update_graph(input):
        df = pd.DataFrame(input)
        return px.scatter(df)
            
    
