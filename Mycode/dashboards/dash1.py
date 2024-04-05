from .base_dashboard import Base_dashboard
from dash import Input, Output, State
from Mycode.economic_data import Economic_data
import plotly.express as px
from dash import dcc
from dash import html
import pandas as pd 
def create_dash1(requests_pathname_prefix):
    dash = Base_dashboard(requests_pathname_prefix, "Курсы валют")
    
    dropdown_curses = dcc.Dropdown(
        options=Economic_data.get_name_curses(),
        value=[Economic_data.get_short_name_curses()[0]],
        id = 'dropdown_curses',
        multi=True,
        clearable=False,
        optionHeight=50,
        )
    dop_layout = html.Div(children=[
        dropdown_curses,
        dcc.Graph(id="graph"),
        ])
    
    dash.set_layout(dop_layout, "Курсы валют")
    dash.init_callbacks(UI)
    return dash.app

def UI(app):
    @app.callback(
    Output('graph', 'figure'),
    Input('button_set_date', 'n_clicks'),
    State('date_start', "date"),
    State('date_end', "date"),
    State('dropdown_curses', 'value'),
    prevent_initial_call = False
    )
    def update_date(count_click, str_start, str_end, curses):
        if curses == []:
            return px.line()
        
        data = [Economic_data.select_currency_exchange_rate(curse, str_start, str_end).assign(name=curse) for curse in curses]
        df = pd.concat(data)
        
        return px.line(df, x='date', y='rate', color='name', template='plotly_dark')
    
