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
        value=Economic_data.get_short_name_curses()[0],
        id = 'dropdown_curses',
        multi=True,
        clearable=False,
        optionHeight=50,
        )
    dop_layout = html.Div(children=[
        dcc.Graph(id="base_graph", figure=px.scatter()),
        dropdown_curses
        ])
    
    dash.set_layout(dop_layout, "Курсы валют")
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
        # date_start = datetime.strptime(str_start, '%Y/%m/%d').date()
        # date_end = datetime.strptime(str_end, '%Y/%m/%d').date()
        # if date_end - date_start <= timedelta(days=5):
        #     return no_update
        fig = px.line()
        if curses == []:
            return fig
        if isinstance(curses, str):
            #df = Economic_data.currency_exchange_rate(curses, str_start, str_end)
            dates = ["01.02.2024", "02.02.2024", "03.02.2024", "04.02.2024", "05.02.2024"]
            rates = [1, 3, 5, 10, 7]
            df = pd.DataFrame({'date': dates, 'rate': rates})
            fig.add_scattergl(x=df['date'], y=df['rate'], name=curses)
        else:
            for curse in curses:
                df = Economic_data.currency_exchange_rate(curse, str_start, str_end)
            fig.add_scattergl(x=df['date'], y=df['rate'], name=curse)
            
        return fig
    
