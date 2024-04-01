import dash
from dash import dash_table
from dash import dcc
from dash import html
from .templates.baseDash import html_layout
import pandas as pd
import plotly.express as px

def init_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/dash/",
        external_stylesheets=[
            "https://fonts.googleapis.com/css?family=Lato"
        ],
    )

    df = pd.DataFrame({'x':[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'y':[2, 4, 6, 10, 16, 26, 42, 68, 110, 178]})

    dash_app.index_string = html_layout

    dash_app.layout = html.Div(
        children=[
           dcc.Graph(id="baseGraph", figure=px.scatter(df, x='x', y='y'))
        ],
        id="dash-container",
    )
    return dash_app.server


