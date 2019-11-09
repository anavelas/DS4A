# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 17:45:30 2019

@author: Anita
"""
# ============================================================================== #

# Librerías y Bases de datos

# ============================================================================== #

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import dash_table
    
from sqlalchemy import create_engine

#engine = create_engine('postgresql://postgres:Anita19802605@database-1.czojagk85rh7.us-east-2.rds.amazonaws.com/trades')
#df = pd.read_sql('SELECT * from "Trade"', engine.connect(), parse_dates=('Entry time'))
    
    
    
    

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/uditagarwal/pen/oNvwKNP.css', 'https://codepen.io/uditagarwal/pen/YzKbqyV.css'])
from sqlalchemy import create_engine

engine = create_engine('postgresql://miruza:miruza123@database-1.czojagk85rh7.us-east-2.rds.amazonaws.com/postgres')
df = pd.read_sql("SELECT * from trade1", engine.connect(), parse_dates=('entrytime',))

# ============================================================================== #
# Funciones de inicio
# ============================================================================== #
def filter_df(df,exchange,Margin,strat_date,end_date):
    return df[(df['exchange'] == exchange) & (df['margin'] == int(Margin))  & 
             ((df['entrytime'] >= strat_date) &  (df['entrytime'] <= end_date))]
def calc_btc_returns(dff):
    btc_start_value = dff.tail(1)['btcprice'].values[0]
    btc_end_value = dff.head(1)['btcprice'].values[0]
    btc_returns = (btc_end_value * 100/ btc_start_value)-100
    return btc_returns
def calc_strat_returns(dff):
    start_value = dff.tail(1)['exitbalance'].values[0]
    end_value = dff.head(1)['entrybalance'].values[0]
    returns = (end_value * 100/ start_value)-100
    return returns
def calc_returns_over_month(dff):
    out = []
    dff['YearMonth'] = df['entrytime'].dt.strftime('%Y-%m')
    for name, group in dff.groupby('YearMonth'):
        exit_balance = group.head(1)['exitbalance'].values[0]
        entry_balance = group.tail(1)['entrybalance'].values[0]
        monthly_return = (exit_balance*100 / entry_balance)-100
        out.append({
            'month': name,
            'entry': entry_balance,
            'exit': exit_balance,
            'monthly_return': monthly_return
        })
    return out

# ============================================================================== #

# Layout 

# ============================================================================== #
app.layout = html.Div(children=[
    html.Div(
            children=[
                html.H2(children="Bitcoin Leveraged Trading Backtest Analysis", className='h2-title'),
            ],
            className='study-browser-banner row'
    ),
    html.Div(
        className="row app-body",
        children=[
            html.Div(
                className="twelve columns card",
                children=[
                    html.Div(
                        className="padding row",
                        children=[
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select exchange",),
                                    dcc.RadioItems(
                                        id="exchange-select",
                                        options=[
                                            {'label': label, 'value': label} for label in df['exchange'].unique()
                                        ],
                                        value='Bitmex',
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            # Leverage Selector
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Leverage"),
                                    dcc.RadioItems(
                                        id="leverage-select",
                                        options=[
                                            {'label': str(label), 'value': str(label)} for label in df['margin'].unique()
                                        ],
                                        value='1',
                                        labelStyle={'display': 'inline-block'}
                                    ),
                                ]
                            ),
                            html.Div(
                                className="three columns card",
                                children=[
                                    html.H6("Select a Date Range"),
                                    dcc.DatePickerRange(
                                        id="date-range",
                                        display_format="MMM YY",
                                        start_date=df['entrytime'].min(),
                                        end_date=df['entrytime'].max()
                                    ),
                                ]
                            ),
                            html.Div(
                                id="strat-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="strat-returns", className="indicator_value"),
                                    html.P('Strategy Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                            html.Div(
                                id="market-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="market-returns", className="indicator_value"),
                                    html.P('Market Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                            html.Div(
                                id="strat-vs-market-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="strat-vs-market", className="indicator_value"),
                                    html.P('Strategy vs. Market Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                        ]
                )
        ]),
        html.Div(
            className="twelve columns card",
            children=[
                dcc.Graph(
                    id="monthly-chart",
                    figure={
                        'data': []
                    }
                )
            ]
        ), 
            
    html.Div(
                className="padding row",
                children=[
                    html.Div(
                        className="six columns card",
                        children=[
                            dash_table.DataTable(
                                id='table',
                                columns=[
                                    {'name': 'Number', 'id': 'number'},
                                    {'name': 'Trade type', 'id': 'tradetype'},
                                    {'name': 'Exposure', 'id': 'exposure'},
                                    {'name': 'Entry balance', 'id': 'entrybalance'},
                                    {'name': 'Exit balance', 'id': 'exitbalance'},
                                    {'name': 'Pnl (incl fees)', 'id': 'pnl'},
                               ],
                                style_cell={'width': '50px'},
                                style_table={
                                    'maxHeight': '450px',
                                    'overflowY': 'scroll'
                                },
                            )
                        ]
                    ),
                    dcc.Graph(
                        id="pnl-types",
                        className="six columns card",
                        figure={},
                        style={'width': '590px', 'height':'450px', 'display': 'inline-block', 'vertical-align': 'middle'},
                    ),
                ]
            ),
            html.Div(
                className="padding row",
                children=[
                    dcc.Graph(
                        id="daily-btc",
                        className="six columns card",
                        figure={},
                        style={'width': '590px', 'height':'450px', 'display': 'inline-block', 'vertical-align': 'middle'},
                    ),
                    dcc.Graph(
                        id="balance",
                        className="six columns card",
                        figure={},
                        style={'width': '590px', 'height':'450px', 'display': 'inline-block', 'vertical-align': 'middle'},
                    )
                ]
            )
        ]
    )        
])
# ============================================================================== #
# Servidor - Actualizador
# ============================================================================== #
# Actualización gráfico
@app.callback(
        [dash.dependencies.Output('monthly-chart', 'figure'),
         dash.dependencies.Output('market-returns','children'),
         dash.dependencies.Output('strat-returns','children'),
         dash.dependencies.Output('strat-vs-market','children')],
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),

    )
)
def update_monthly(exchange, leverage, start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    data = calc_returns_over_month(dff)
    btc_returns = calc_btc_returns(dff)
    strat_returns = calc_strat_returns(dff)
    strat_vs_market = strat_returns - btc_returns

    return ({
        'data': [
            go.Candlestick(
                open=[each['entry'] for each in data],
                close=[each['exit'] for each in data],
                x=[each['month'] for each in data],
                low=[each['entry'] for each in data],
                high=[each['exit'] for each in data]
            )
        ],
        'layout': {
            'title': 'Overview of Monthly performance'
        }
    }, f'{btc_returns:0.2f}%', f'{strat_returns:0.2f}%', f'{strat_vs_market:0.2f}%')

# grafico pnl-types

@app.callback(
        dash.dependencies.Output('pnl-types', 'figure'),
     (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),

    )
)

def update_barchart (exchange, leverage,start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    dff['Date'] = pd.to_datetime(dff['entrytime'].dt.strftime('%Y-%m-%d'))
    
    # filter trade types
    dff_lg = dff[dff['tradetype']=='Long']
    dff_st = dff[dff['tradetype']=='Short']
    
    return {
        'data':[
            go.Bar(
            x = dff_lg['entrytime'],
            y = dff_lg['pnl'].values.tolist(),
            name = 'Long',
            marker = {'color':'red'}),
            go.Bar(
            x = dff_st['entrytime'],
            y = dff_st['pnl'].values.tolist(),
            name = 'Short',
            marker = {'color':'black'})         
        ],
    'layout':{'title':'Pnl vs Trade Type',
              'type':'date'}}

## # grafico daily-btc

@app.callback(
        dash.dependencies.Output('daily-btc', 'figure'),
     (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),

    )
)

def update_barchart (exchange, leverage,start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    dff['Date'] = pd.to_datetime(dff['entrytime'].dt.strftime('%Y-%m-%d'))
    
    
    return {
        'data':[
            go.Line(
            x = dff['entrytime'],
            y = dff['btcprice'].values.tolist(),
            marker = {'color':'blue'})
                 
        ],
    'layout':{'title':'Daily BTC Price',
              'type':'date'}}

## # grafico balance

@app.callback(
        dash.dependencies.Output('balance', 'figure'),
     (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),

    )
)

def update_barchart (exchange, leverage,start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    dff['Date'] = pd.to_datetime(dff['entrytime'].dt.strftime('%Y-%m-%d'))
    

    
    return {
        'data':[
            go.Line(
            x = dff['entrytime'],
            y = dff['entrybalance'].values.tolist(),
            marker = {'color':'blue'})
                 
        ],
    'layout':{'title':'Balance overtime',
              'type':'date'}}



## Actualización de la tabla
@app.callback(
    dash.dependencies.Output('table', 'data'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),
    )
)
def update_table(exchange, leverage, start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    return dff.to_dict('records')




# ============================================================================== #


# ============================================================================== #
# Ejecutor

if __name__ == "__main__":
    app.run_server(debug=True,host = "0.0.0.0")

# ============================================================================== #
