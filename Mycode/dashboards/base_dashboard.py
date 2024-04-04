import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import plotly.express as px
from Mycode.economic_data import Economic_data
from datetime import datetime, timedelta

class Base_dashboard(object):
    
    def __init__(self, pathname, name="dash"):
        self.name = name

        dash_app = dash.Dash(requests_pathname_prefix=pathname, update_title='обновление...')
        dash_app.index_string = open("MyCode/templates/dash.html", encoding='UTF-8').read() # шапка и подвал dashboard-а
        self.app = dash_app
    
    def set_layout(self, div_with_graphs_and_dropdown, text):
        text = html.H1(text, className='name_graph', style={'textAlign':'center'})
        date_start = dcc.DatePickerSingle(
            className='date_field',
            id="date_start",
            is_RTL=True,
            display_format='DD.MM.YYYY',
            date= Economic_data.get_start_date()
        )
        date_end = dcc.DatePickerSingle(
            className='date_field',
            id="date_end",
            is_RTL=True,
            display_format='DD.MM.YYYY',
            date=(datetime.now() - timedelta(days=1)).date()
        )
        button_set_date = html.Button(id="button_set_date", children="обновить график", className='button_create')
    
        layout = html.Div(
            children=[
                text,
                html.Div(className='date_punel', children=[date_start, date_end, button_set_date]),
                html.Div(className = "graph_and_dropdown", children=[div_with_graphs_and_dropdown])
            ]
        )
        
        self.app.layout = layout
       
    def init_callbacks(self, func):        
        func(self.app)
