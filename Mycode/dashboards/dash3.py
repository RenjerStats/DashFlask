from .base_dashboard import Base_dashboard
from dash import Input, Output, State
from Mycode.economic_data import Economic_data
import plotly.express as px
from dash import dcc
from dash import html

def create_dash3(requests_pathname_prefix):
    dash = Base_dashboard(requests_pathname_prefix, "Ставка Центробанка")
    
    dropdown_curses = dcc.Dropdown(
        options=["ключевая ставка ЦБ", "инфляция"],
        value="ключевая ставка ЦБ",
        id = 'dropdown_curses',
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
    prevent_initial_call = False
    )
    def update_date(count_click, str_start, str_end, curses):
        str_start = Economic_data.convert_date(str_start)
        str_end = Economic_data.convert_date(str_end)
        fig = px.line()
        if curses == []:
            return fig
        
        if isinstance(curses, str):
            if curses == "инфляция":
                df = Economic_data.select_inflation_rate(str_start, str_end)
            else:
                df = Economic_data.select_central_bank_rate(str_start, str_end)
            fig.add_scattergl(x=df['date'], y=df['rate'], name=curses)
        else:
            df = Economic_data.select_inflation_rate(str_start, str_end)
            fig.add_scattergl(x=df['date'], y=df['rate'], name="инфляция")
            df = Economic_data.select_central_bank_rate(str_start, str_end)
            fig.add_scattergl(x=df['date'], y=df['rate'], name="ставка ЦБ")
            
        return fig
    
