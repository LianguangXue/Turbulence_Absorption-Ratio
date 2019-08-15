from Data_Require import *
import pandas as pd
import numpy as np
from statsmodels.distributions.empirical_distribution import ECDF
import statsmodels.api as sm
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
#define a function to transfrom the score from -1 to 1
def transform_score(X):
    Xmin = np.min(X)
    Xmax = np.max(X)
    temp = []
    for x in X:
        temp.append((2*x-Xmin-Xmax)/(Xmax-Xmin))
    return temp



if __name__ =='__main__':
    py.tools.set_credentials_file(username='GlobalAI', api_key="8z3hbIL0C6X2EluqlOT7")
    tickers = ['GOOG','AAPL','CSCO','FB','INTC','MSFT']
    today = dt.today().strftime("%Y-%m-%d")
    start = '2000-01-01'
    end = today
    big_cap = get_Data(tickers,start,end)
    tb = norm_turb(big_cap,cutoff=1/5)

    #generate X,y for regression
    X1,y1,date1 = generate_XY(big_cap,'AAPL',tb)
    X1, y1 = lin_regress_XY(X1,y1,lag=5)
    X1 = sm.add_constant(X1)
    model1 = sm.OLS(y1, X1).fit()
    model1.predict(X1)
    score = transform_score(model1.predict(X1))

    #plot online use plotly
    trace0 = go.Bar(
        x= ['a',date1[-1],'b'],
        y =[0,score[-1],0],
        name =  'Score for last day')
    #trace1 = go.Bar(
    #    x = date1[-10:],
    #    y  =score[-10:],
    #    name = 'Last Five Days '
    #)
    data = [trace0]

    layout = dict(title='Turbulence Score',
                  shapes=[{'type': 'line','y0':-1,'y1': -1,'x0':'a',
                                  'x1':'b','xref':'x1','yref':'y1',
                                  'line': {'color': 'red','width': 1}},
                                 {'type': 'line','y0':1,'y1': 1,'x0':'a',
                                  'x1':'b','xref':'x1','yref':'y1',
                                  'line': {'color': 'green','width': 1}}])
    fig = go.Figure(data = data,layout = layout)
    py.plotly.plot(fig,filename="Macro/Turbulence Score")





