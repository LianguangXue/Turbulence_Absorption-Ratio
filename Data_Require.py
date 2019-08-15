from datetime import datetime as dt
from datetime import timedelta
import numpy as np
import pandas as pd
import datetime
import quandl as q
from numpy import linalg as LA
from scipy.stats import norm
from numpy.linalg import inv
from numpy.linalg import cond

#get weekly time list 
def get_weekday(start,end):
    s = pd.date_range(start, end, freq='D').to_series()
    result = list(s.dt.dayofweek[s.dt.dayofweek<=4].index)
    return result


# log Return data download function
def get_return(stock, start, end):
    ## input "stock symbol", "start date", "end date", output daily return in dataframe
    q.ApiConfig.api_key = 'Ufux_HxUXZKAgFjxWhGi'
    stock = 'EOD/'+ stock
    #get adj_close price
    close = q.get(stock,start_date=start, end_date=end, collapse = "daily", column_index='11')
    dat = pd.DataFrame(index = get_weekday(start,end))
    dat.index.name = 'Date'
    dat = pd.concat([dat,close],sort=False,axis=1)
    dat = dat.fillna(method='backfill')
    n = len(dat)
    temp = 0
    ret=[]
    for i in range(5,n):
        close_now = dat.iloc[i,:].values[0]
        temp = pd.to_datetime(dat.index[i].to_pydatetime()-timedelta(days=7))
        close_before = dat.loc[temp].values[0]
        ret.append(np.log(close_now)-np.log(close_before))
    dat = dat.iloc[5:,:]
    
    dat['log_ret'] = ret
    return dat


# Pick the ticker(longest) that has the most data (for the date to be longest)
def get_Data(tickers, start, end):

    longest = 0
    long = 0
    for i in tickers:
        ereturn = get_return(i, start, end)
        if len(ereturn) >= long:
            long = len(ereturn)
            longest = i

    # Generate the return matrix
    Data = get_return(longest, start, end)
    dat = pd.DataFrame(index= Data.index)
    for i in tickers:
        step = get_return(i, start, end)['log_ret'].values
        dat[i] = step

    dat = dat.fillna(0)
    dat = dat.iloc[:-1,:]
    return dat


# Function for measure of Turbulence
def norm_turb(Data,cutoff=1/5):
    Tur = []
    
    # before cutoff of total data "cheating" mean and covariance matrix
    len_all = len(Data)
    len_before = int(len(Data)*cutoff)
    Data_before = Data.iloc[0:len_before]
    data0 = np.array(Data_before).T
    cov0 = np.cov(data0)

    if np.isfinite(cond(cov0)):
        covinv0 = inv(cov0)
        mean0 = np.array(np.mean(Data_before))
    else:
        for i in range(len(Data_before),len(Data)):
            if (any(x==0 for x in Data.iloc[i])==0):
                Data_before1 = Data.iloc[0:i+100]
                data1 = np.array(Data_before1).T
                cov1 = np.cov(data1)
                covinv0 = np.matrix(inv(cov1))
                mean0 = np.array(np.mean(Data_before1))
                len_before = int(len(Data_before1))
                Data_before = Data_before1
                break
  
    for i in range(0,len_before):
        x0 = np.matrix(Data.iloc[i]-mean0)
        y0 = x0*covinv0*x0.T
        Tur.append(y0[0,0])
    # after curoff data, real historical
    for i in range(len_before,len_all):
        Data_aft = Data.iloc[0:i-1]
        data = np.array(Data_aft).T
        cov = np.cov(data)
        covinv = np.matrix(inv(cov))
        mean = np.array(np.mean(Data_aft))
        x = np.matrix(Data.iloc[i]-mean)
        y = x*covinv*x.T
        Tur.append(y[0,0])
        #any([math.isnan(x) for x in Tur])
    # Generate the normalized Turbulence
    Z_tur = (Tur-np.mean(Tur))/np.std(Tur)
    NormT = norm.cdf(Z_tur)
    
    return NormT   


# Function for normalized AR
def norm_AR(Data,tickers,windows=500):
    date = Data.index.tolist()
    
    #df of numerator with all sectors
    #weighted moving average (WMA) for variance calculation
    eigen_list = []
    for i in range(len(date)-windows):
        Data1 = np.array(Data.iloc[i:i+windows]).T
        Cov = np.cov(Data1)
        w, v = LA.eig(Cov)
        eigen_list.append(w)

    df_eigen = pd.DataFrame(eigen_list)
    ewm_eigen = df_eigen.ewm(halflife=windows/2).mean()
    num = ewm_eigen.iloc[:,0:round(len(tickers)/5)].sum(axis=1)
    #num = df_eigen.iloc[:,0:round(len(tickers)/5)].sum(axis=1)
    
    #df of denominator with all sectors
    #exponentially weighted moving average (EWMA) for variance calculation
    Data_2 = Data**2
    ewma_data_2 = Data_2.ewm(halflife=windows/2,adjust=False).mean()
    # ewma var matrix (denom add up to 8 tickers on each trading day)
    denom = ewma_data_2.iloc[windows:len(num)+windows].sum(axis=1)

    #AR=num/denom,standard normalization
    AR = np.array(num)/np.array(denom)
    norm_AR = norm.cdf((AR-np.mean(AR))/np.std(AR))
    
    return norm_AR

#Define a fucnction to get turbulence data for different market
def get_tb_dataframe(market_dict,start,end):
    tb_dict={}
    for market in market_dict.keys():
        print('Start request',market.replace('_',' '),'data')
        tickers = market_dict[market]
        Data = get_Data(tickers, start, end)
        date = Data.index.tolist()
        norm_tb = norm_turb(Data)
        mv_tb = pd.DataFrame({'norm_tb':norm_tb}).rolling(window=22).mean().values[22:]
        date_tb = date[22:]
        dat_tb = pd.DataFrame({'date':date_tb,market:[i[0] for i in list(mv_tb)]})
        tb_dict[market] = dat_tb
    temp = tb_dict[list(tb_dict.keys())[0]]
    for market in list(tb_dict.keys())[1:]:
        temp = temp.merge(tb_dict[market],how = 'outer',on='date')
    return temp

#Define a function to get Absorption Ratio for different asset
def get_ar_dataframe(asset_list,start,end):
    tickers = asset_list
    Data = get_Data(tickers,start, end)
    date = Data.index.tolist()
    date_ar = date[500:]
    norm_ar = norm_AR(Data,tickers,500)
    dat = pd.DataFrame({'date':date_ar,'AbsorptionRatio':norm_ar})
    return dat

#get correlation matrix for a market 
def correlation_in_market(tickers,start,end):
    X = get_Data(tickers, start, end)
    corr = X.corr()
    html= corr.style.background_gradient(cmap='coolwarm',axis=None).render()
    return corr,html
