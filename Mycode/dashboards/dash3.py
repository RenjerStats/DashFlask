﻿from .base_dashboard import Base_dashboard
from dash import Input, Output, State
from Mycode.economic_data import Economic_data
import plotly.express as px
from dash import dcc
from dash import html
import pandas as pd

def create_dash3(requests_pathname_prefix):
    dash = Base_dashboard(requests_pathname_prefix, "Ставка Центробанка")
    
    dropdown_curses = dcc.Dropdown(
        options=["ключевая ставка ЦБ", "инфляция"],
        value=["ключевая ставка ЦБ"],
        id = 'dropdown_curses',
        multi=True,
        clearable=False,
        optionHeight=50,
        )
    dop_layout = html.Div(children=[
        dropdown_curses,
        dcc.Graph(id="base_graph", figure=px.scatter()),
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
    prevent_initial_call = False
    )
    def update_date(count_click, str_start, str_end, curses):
        if curses == '':
            return px.line()
        
        data = []
        if 'ключевая ставка ЦБ' in curses: data.append(Economic_data.select_central_bank_rate(str_start, str_end).assign(name="Курс ЦБ"))
        if 'инфляция' in curses: data.append(Economic_data.select_inflation_rate(str_start, str_end).assign(name="инфляция"))
        df = pd.concat(data)
        
        return px.line(df, x='date', y='rate', color='name', template='plotly_dark')
    