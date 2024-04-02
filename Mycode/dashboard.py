import dash
from dash import Input, Output, State, no_update
from dash import dcc
from dash import html
import plotly.express as px
from datetime import date, timedelta

from .economic_data import Economic_data

economic_data = Economic_data("2016/06/21", "2017/06/21")
def init_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/dash/",
        external_stylesheets=["https://fonts.googleapis.com/css?family=Lato"],
    )

    dash_app.index_string = open("MyCode/templates/dash.html", encoding='UTF-8').read()
    dash_app.layout = get_layout()
        
    init_callbacks(dash_app)
    return dash_app.server


def get_layout(df = []):
    date_start = dcc.DatePickerSingle(
        id="date_start",
        is_RTL=True,
        date=date(2016, 6, 21)
    )
    date_end = dcc.DatePickerSingle(
        id="date_end",
        is_RTL=True,
        date=date(2017, 6, 21)
    )
    button_set_date = html.Button(id="button_set_date", children="установить диапазон")
    
    dropdown_groups = dcc.Dropdown(
        options={
        'kurs': 'Курсы валют',
        'akcii': 'Акции крупных компаний',
        'stafka': 'Ставка центробанка'
        },
        value='kurs',
        id = 'dropdown_groups',
        multi=False,
        clearable=False,
        optionHeight=50,
        )
    dropdown_curses = dcc.Dropdown(
        [],
        value=[],
        id = 'dropdown_curses',
        multi=True,
        clearable=False,
        optionHeight=50,
        )
    
    layout = html.Div(
        children=[
            dcc.Graph(id="base_graph", figure=px.scatter(df)),
            date_start, date_end, button_set_date,
            dropdown_groups, dropdown_curses
        ]
    )
    return layout

def init_callbacks(app):
    @app.callback(
        Output('dropdown_curses', 'options'),
        Output('dropdown_curses', 'value'),
        Output('base_graph', 'figure'),
        Input('dropdown_groups', 'value'),
        prevent_initial_call=False
        )
    def update_graph1(group):
        curses = []
        if group == "kurs":
            curses = economic_data.names_exchange_rate
        print(curses, group)
        fig = px.line()
        if len(curses) != 0: fig = px.scatter(economic_data.currency_exchange_rate(curses[0]), name=curses[0])
        
        return curses, curses[0], fig
    
    @app.callback(
        Output('base_graph', 'figure'),
        Input('dropdown_curses', 'value'),
        prevent_initial_call=True
        )
    def update_graph2(curses):
        fig = px.line()
        for curse in curses:
            fig.add_scattergl(economic_data.currency_exchange_rate(curse), name=curse)
            
        return fig
    
    @app.callback(
        Output('base_graph', 'figure'),   
        Input('dropdown_curses', 'value'),    
        State('date_start', "date"),
        State('date_end', "date"),
        State('dropdown_curses', 'value'),
        prevent_initial_call = True
        )
    def update_graph2(count_click, dateStart, dateEnd, curses):
        if dateEnd - dateStart <= timedelta(days=5):
            return no_update
        
        str_dateStart = dateStart.strftime('%Y/%m/%d')
        str_dateEnd = dateEnd.strftime('%Y/%m/%d')
        economic_data.set_dates(str_dateStart, str_dateEnd)
        
        fig = px.line()
        for curse in curses:
            fig.add_scattergl(economic_data.currency_exchange_rate(curse), name=curse)
            
        return fig
        

        
    
            
    
