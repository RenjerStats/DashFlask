from datetime import timedelta
from re import template

from plotly.graph_objs import Layout
from .base_dashboard import Base_dashboard
from dash import Input, Output, State
from Mycode.economic_data import Economic_data
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from dash import html
import pandas as pd

from datetime import datetime, timedelta
def create_dash2(requests_pathname_prefix):
    dash = Base_dashboard(requests_pathname_prefix, "Курсы акций")
    
    dropdown_curses = dcc.Dropdown(
        options=Economic_data.get_name_companies(),
        value=[Economic_data.get_short_name_companies()[0]],
        id = 'dropdown_curses',
        multi=True,
        clearable=False,
        optionHeight=50,
        )
    
    dropdown_curse = dcc.Dropdown(
        options=Economic_data.get_name_companies(),
        value=Economic_data.get_short_name_companies()[0],
        id = 'dropdown_curse',
        multi=False,
        clearable=False,
        optionHeight=50,
        )
    
    dropdown_date = dcc.Dropdown(
        options=["за неделю", "за месяц", "за год", "за все время"],
        value="за год",
        id = 'dropdown_date',
        multi=False,
        clearable=False,
        optionHeight=50,
        )
    graph1 = dcc.Graph(id = "base_graph")
    dop_layout = html.Div(children=[
                html.Div([dropdown_curses, graph1], className='graph_dropdown'),
        html.Div([dropdown_curse, dropdown_date, dcc.Graph(id = 'histogram')], className='graph_dropdown'),
        ], className='row_graph')
    
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
    prevent_initial_call = False
    )
    def update_graph(count_click, str_start, str_end, curses):
        str_start = Economic_data.convert_date(str_start)
        str_end = Economic_data.convert_date(str_end)
        if curses == []:
            return px.line()
        
        data = [Economic_data.select_shares_rate(curse, str_start, str_end).assign(name=curse) for curse in curses]
        df = pd.concat(data)
        
        return px.line(df, x='date', y='rate', color='name', template='plotly_dark')
    
    @app.callback(
    Output('histogram', 'figure'),
    Input('dropdown_curse', 'value'),
    Input('dropdown_date', 'value'),
    prevent_initial_call = False
    )
    def update_histogram(curse, str_date):  
        str_end = (datetime.now() - timedelta(days=1)).date().strftime('%d-%m-%Y')
        if str_date == "за неделю":
            str_start = (datetime.now() - timedelta(weeks=1)).date().strftime('%d-%m-%Y')
        elif str_date == "за месяц":
            str_start = (datetime.now() - timedelta(days=30)).date().strftime('%d-%m-%Y')
        if str_date == "за год":
            str_start = (datetime.now() - timedelta(days=365)).date().strftime('%d-%m-%Y')
        if str_date == "за все время":
            str_start = (datetime.now() - timedelta(days=365*5)).date().strftime('%d-%m-%Y')
        
        df = Economic_data.select_shares_rate_percent(curse, str_start, str_end)    

        fig = go.Figure(data=go.Bar(
                x=df['date'],
                y=df['rate'],
                marker_color=df['color'].to_list(),
            ),
            layout=go.Layout(height=350, )
        )   
        fig.update_layout(template="plotly_dark")
        return fig
    

    
