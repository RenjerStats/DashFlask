from dash import Input, Output, State
from dash import dcc
from dash import html

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from .base_dashboard import BaseDashboard
from ..parser import select_shares_rate
from ..CONST import SHARES_NAMES


def create_dash2(requests_pathname_prefix):
    dash = BaseDashboard(requests_pathname_prefix, "Курсы акций")
    dropdown_curses = dcc.Dropdown(
        options=SHARES_NAMES,
        value=[list(SHARES_NAMES.keys())[0]],
        id='dropdown_curses',
        multi=True,
        clearable=False,
        optionHeight=50,
    )
    dop_layout = html.Div(children=[
        dcc.Graph(id="base_graph", figure=px.scatter()),
        dropdown_curses
    ])
    dash.set_layout(dop_layout, "Курсы акций")
    dash.init_callbacks(UI)
    return dash.app


def UI(app):
    @app.callback(
        Output('base_graph', 'figure'),
        Input('button_set_date', 'n_clicks'),
        State('date_start', "date"),
        State('date_end', "date"),
        State('dropdown_curses', 'value'),
        prevent_initial_call=False
    )
    def update_date(count_click, str_start, str_end, curses):
        str_start = datetime.strptime(str_start, '%Y-%m-%d').strftime('%d-%m-%Y')
        str_end = datetime.strptime(str_end, '%Y-%m-%d').strftime('%d-%m-%Y')
        if not curses:
            return px.line()
        data = [select_shares_rate(curse, str_start, str_end).assign(name=curse) for curse in curses]
        df = pd.concat(data)
        return px.line(df, x='date', y='rate', color='name')
