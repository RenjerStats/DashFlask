import dash
from dash import Input, Output, State
from dash import dcc
from dash import html
import plotly.express as px
from Mycode.economic_data import Economic_data
from datetime import datetime

class Base_dashboard(object):
    
    def __init__(self, pathname, name="dash"):
        self.name = name
        external_stylesheets = [
            'https://codepen.io/chriddyp/pen/bWLwgP.css',
            {
                'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
                'rel': 'stylesheet',
                'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
                'crossorigin': 'anonymous'
            }
        ]


        dash_app = dash.Dash(requests_pathname_prefix=pathname, external_stylesheets=external_stylesheets, update_title='обновление...')
        dash_app.index_string = open("MyCode/templates/dash.html", encoding='UTF-8').read() # шапка dashboard-а
        self.app = dash_app
    
    def set_layout(self, div_with_graphs_and_dropdown, text):
        text = html.H1(text)
        date_start = dcc.DatePickerSingle(
            id="date_start",
            is_RTL=True,
            display_format='DD.MM.YYYY',
            date=Economic_data.get_start_date()
        )
        date_end = dcc.DatePickerSingle(
            id="date_end",
            is_RTL=True,
            display_format='DD.MM.YYYY',
            date=Economic_data.get_today_date()
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
