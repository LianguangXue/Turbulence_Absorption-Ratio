from Data_Require import *
import pandas as pd
import numpy as np
from statsmodels.distributions.empirical_distribution import ECDF
import statsmodels.api as sm
from numpy.linalg import cond
from plotly import tools
import plotly as py
import plotly.graph_objs as go

def cut_use(list1):
    n = len(list1)
    temp = 0
    for i in range(n):
        if list1[i] != 0:
            temp = i
            break;
    return list1[temp:],temp


def generate_XY(data,ticker,index):
    ret,temp = cut_use(data[ticker].values)
    ecdf = ECDF(ret)
    n_ret = len(ret)
    y = ecdf(ret)
    X = index[-n_ret:]
    date_list = list(data.index)
    date_list = date_list[temp:]
    date_list = date_list[-n_ret:]
    return X,y,date_list
#use lag 
def lin_regress_XY(X,y,lag=1):
    X = X[:-lag]
    y = y[lag:]
    assert(len(X)==len(y))
    return X,y

def transform_score(X):
    Xmin = np.min(X)
    Xmax = np.max(X)
    temp = []
    for x in X:
        temp.append((2*x-Xmin-Xmax)/(Xmax-Xmin))
    return temp


if __name__=="__main__":
    tickers = ['GOOG','AAPL','CSCO','FB','INTC','MSFT']
    today = dt.today().strftime("%Y-%m-%d")
    start = '2005-01-01'
    end = today
    big_cap = get_Data(tickers,start,end)

    ar = norm_AR(big_cap, tickers)

    X2,y2,date2 = generate_XY(big_cap,'AAPL',ar)

    y2 = y2[500:]

    X2, y2 = lin_regress_XY(X2,y2,lag=1)

    X2 = sm.add_constant(X2)
    model2 = sm.OLS(y2, X2).fit()

    score = transform_score(model2.predict(X2))
    #Plot online plot
    py.tools.set_credentials_file(username='GlobalAI', api_key="8z3hbIL0C6X2EluqlOT7")
    trace0 = go.Bar(
        x= date2[-1:],
        y =score[-1:],
        name =  'Score for last day')

    data = [trace0]

    layout = dict(title='Absorption Ratio Score',
                  shapes=[{'type': 'line','y0':-1,'y1': -1,'x0':'a',
                                  'x1':'b','xref':'x1','yref':'y1',
                                  'line': {'color': 'red','width': 1}},
                                 {'type': 'line','y0':1,'y1': 1,'x0':'a',
                                  'x1':'b','xref':'x1','yref':'y1',
                                  'line': {'color': 'green','width': 1}}])
    fig = go.Figure(data = data,layout = layout)
    py.plotly.plot(fig,filename="Macro/Absorption Ratio Score")





