import dash
import dash_core_components as dcc
import dash_html_components as html
from Data_Require import *
import plotly.graph_objs as go
from plotly import tools
from dash.dependencies import Input, Output
from flask import Flask
server =Flask('my app')

warnings.filterwarnings(action="ignore", message="unclosed",
                         category=ResourceWarning)


Asset_Classes= ['SPY', 'EEM', 'EFA', 'EMB', 'IPE', 'DBC', 'GLD', 'USO', 'RWO', 'GII', 'DBV']
US_Sectors = ['IYC','IYE','IYF','IYH','IYJ','IYK','IYM','IYR','IYW','IYZ']
Developed_Countries_Stock = ['EWA', 'EWU', 'EWC', 'EWH', 'EWL', 'EWD', 'EWS', 'EWJ', 'EWG', 'EWI', 'EWP', 'EWQ']
Emerging_Markets_Stock = ['EWZ', 'EWW', 'EZA', 'EWY', 'GXC']
Fixed_Income = ['SHY', 'IEI', 'IEF', 'TLH', 'TLT', 'BWX', 'CRED', 'JNK', 'LQD']
FX= ['UUP', 'BZF', 'FXA', 'FXB', 'FXC', 'FXF', 'FXS', 'FXSG', 'FXY']

market_dict = {'Asset_Classes':Asset_Classes,
               'US_Sectors':US_Sectors,
               'Developed_Countries_Stock':Developed_Countries_Stock,
               'Emerging_Markets_Stock': Emerging_Markets_Stock,
               'Fixed_Income':Fixed_Income,
               'FX':FX}

today = dt.today().strftime("%Y-%m-%d")
start = '2000-01-01'
end = today

dat = get_tb_dataframe(market_dict,start,end)
############################################################################
#Create dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash('Turbulence for Different Market', external_stylesheets=external_stylesheets,server = server)
app.layout = html.Div([
    dcc.Graph(id='Turbulence'),
    dcc.Dropdown(
        id='Market',
        options=[
            {'label':'Asset Classes','value':'Asset_Classes'},
            {'label':'US Sectors','value':'US_Sectors'},
            {'label':'Developed Countries Stock','value':'Developed_Countries_Stock'},
            {'label':'Emerging Markets Stock','value':'Emerging_Markets_Stock'},
            {'label':'Fixed Income','value':'Fixed_Income'},
            {'label':'FX','value':'FX'}
        ],
        value='Asset_Classes'
    )
])


@app.callback(
    Output('Turbulence', 'figure'),
    [Input('Market', 'value')])


def update_graph(market_name):
    traces = []
    traces.append(go.Scatter(
        x=dat['date'],
        y=dat[market_name].values,
        opacity=0.7,
        marker={'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
               },
        name='Turbulence'
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            title='Turbulence for Different Market'
        )
    }


if __name__ == '__main__':
    app.run_server()
