from dash import Input, Output, State
from dash import dcc
from dash import html

import pandas as pd
import plotly.express as px
from datetime import datetime

from .base_dashboard import BaseDashboard
from ..parser import select_central_bank_rate, select_inflation_rate
from ..CONST import CURRENCY_NAMES


def create_dash3(requests_pathname_prefix):
    dash = BaseDashboard(requests_pathname_prefix, "Ставка Центробанка")
    dropdown_curses = dcc.Dropdown(
        options=["ключевая ставка ЦБ", "инфляция"],
        value=["ключевая ставка ЦБ"],
        id='dropdown_curses',
        multi=True,
        clearable=False,
        optionHeight=50,
    )
    dop_layout = html.Div(children=[
        dcc.Graph(id="base_graph", figure=px.scatter()),
        dropdown_curses
    ])
    dash.set_layout(dop_layout, "Ставка Центробанка")
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
        if curses == '':
            return px.line()
        data = []
        if 'ключевая ставка ЦБ' in curses: data.append(
            select_central_bank_rate(str_start, str_end).assign(name="инфляция"))
        if 'инфляция' in curses: data.append(
            select_inflation_rate(str_start, str_end).assign(name="Курс ЦБ"))
        df = pd.concat(data)
        return px.line(df, x='date', y='rate', color='name')
