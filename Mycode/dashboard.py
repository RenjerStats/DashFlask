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
    df = []

    dash_app.index_string = open("MyCode/templates/dash.html", encoding='UTF-8').read()
    dash_app.layout = get_layout(df)
        
    init_callbacks(dash_app)
    return dash_app.server


def get_layout(df):
    button1 = html.Button(id='buttonCreate', children='курсы валют')
    button2 = html.Button(id='buttonCreate', children='курсы бумаг')
    button3 = html.Button(id='buttonCreate', children='курсы ЦБ')
    
    droplist1 = dcc.Dropdown(
        [1, 2, 3, 5, 7],
        value=2,
        id = 'dropdown1',
        multi=False,
        clearable=False,
        optionHeight=50,
        )
    droplist2 = dcc.Dropdown(
        [2, 4, 6, 8, 10],
        value=[2, 4],
        id = 'dropdown2',
        multi=True,
        clearable=False,
        optionHeight=50,
        )
    
    layout = html.Div(
        children=[
            dcc.Graph(id="base_graph", figure=px.scatter(df)),
            droplist1, droplist2
        ]
    )
    return layout

def init_callbacks(app):
    @app.callback(
        Output('dropdown2', 'options'),
        Output('dropdown2', 'value'),
        Input('dropdown1', 'value'),
        prevent_initial_call=True)
    def update_graph1(val):
        options = [i*val for i in range(1, 5)]
        return options, [options[0], options[1]]
    
    @app.callback(
        Output('base_graph', 'figure'),
        Input('dropdown2', 'value'),
        #prevent_initial_call=True
        )
    def update_graph2(vals):
        print(vals)
        df = pd.DataFrame(vals)
        return px.scatter(df)
            
    
