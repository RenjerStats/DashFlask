﻿import dash
from dash import Input, Output, State
from dash import dcc
from dash import html

import plotly.express as px
from datetime import datetime, timedelta


class BaseDashboard(object):
    def __init__(self, pathname, name="dash"):
        self.name = name
        dash_app = dash.Dash(requests_pathname_prefix=pathname, update_title='обновление...')
        dash_app.index_string = open("scripts/templates/dash.html", encoding='UTF-8').read()
        self.app = dash_app
    
    def set_layout(self, div_with_graphs_and_dropdown, text):
        text = html.H1(text, style={'color':'red'})
        date_start = dcc.DatePickerSingle(
            id="date_start",
            is_RTL=True,
            display_format='DD.MM.YYYY',
            date=datetime.strptime('01.01.2023', "%d.%m.%Y").date()
        )
        date_end = dcc.DatePickerSingle(
            id="date_end",
            is_RTL=True,
            display_format='DD.MM.YYYY',
            date=(datetime.now() - timedelta(days=1)).date()
        )
        button_set_date = html.Button(id="button_set_date", children="обновить график")
    
        layout = html.Div(
            children=[
                text,
                div_with_graphs_and_dropdown,
                date_start, date_end, button_set_date
            ]
        )

        self.app.layout = layout
       
    def init_callbacks(self, func):        
        func(self.app)
