from .base_dashboard import Base_dashboard
from dash import Input, Output, State
from Mycode.economic_data import Economic_data
import plotly.express as px
from dash import dcc
from dash import html

def create_dash1(requests_pathname_prefix):
    dash = Base_dashboard(requests_pathname_prefix, "Курсы валют")
    
    dropdown_curses = dcc.Dropdown(
        options=Economic_data.get_name_curses(),
        value=Economic_data.get_short_name_curses()[0],
        id = 'dropdown_curses',
        multi=True,
        clearable=False,
        optionHeight=50,
        )
    dop_layout = html.Div(children=[
        dcc.Graph(id="graph"),
        dropdown_curses
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
        str_start = Economic_data.convert_date(str_start)
        str_end = Economic_data.convert_date(str_end)
        if curses == []:
            return px.line()
        if isinstance(curses, str):
            df = Economic_data.select_currency_exchange_rate(curses, str_start, str_end)
            return px.line(df, x='date', y='rate')
        else:
            df = [Economic_data.select_currency_exchange_rate(curse, str_start, str_end).assign(name=curse) for curse in curses]
            
        return px.line(df, x='date', y='rate', color='name', symbol="name")
    
