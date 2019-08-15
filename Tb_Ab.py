from Data_Require import *
import warnings
from plotly import tools
import plotly as py
import plotly.graph_objs as go

if __name__=='__main__':
    warnings.filterwarnings(action="ignore", message="unclosed",
                             category=ResourceWarning)



    # Generate the Score Based on the AR data
    # Input the list of tickers here
    # TickersUSsectors = ['IYC','IYE','IYF','IYH','IYJ','IYK','IYM','IYR','IYW','IYZ']
    TickersUSsectors = ['EWA', 'EWU', 'EWC', 'EWH', 'EWL', 'EWD', 'EWS', 'EWJ', 'EWG', 'EWI', 'EWP', 'EWQ']

    tickers = TickersUSsectors
    today = dt.today().strftime("%Y-%m-%d")
    start = '2000-01-01'
    end = today

    # Generate return dataframe
    Data = get_Data(tickers, start, end)
    date = Data.index.tolist()


    tools.set_credentials_file(username='lxue10',api_key="F29SN8EVwOJKhZBoT3wG")


    norm_tb = norm_turb(Data)
    mv_tb = pd.DataFrame({'norm_tb':norm_tb}).rolling(window=22).mean().values[22:]
    date_tb = date[22:]
    date_ar = date[500:]
    norm_ar = norm_AR(Data,tickers,500)



    #Create traces
    trace0 = go.Scatter(
        x = date_tb,
        y = mv_tb,
        mode = 'lines',
        name = 'Turbulence'
    )
    trace1 = go.Scatter(
        x = date_ar,
        y  =norm_ar,
        mode = 'lines',
        name = 'Absorption Ratio'
    )
    fig = tools.make_subplots(rows=2,cols=1)
    fig.append_trace(trace0,1,1)
    fig.append_trace(trace1,2,1)

    fig['layout'].update(title='Turbulence & Absorption Ratio')


    #layout = dict(title='Turbulence',
    #             yaxis=dict(zeroline = False))
    #data = [trace0]
    #fig = go.Figure(data = data,layout = layout)
    py.plotly.plot(fig,filename='Tb_Ar.html')


