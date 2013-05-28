import getdata
import pandas as pd
import portfolio
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas.stats.moments as m

def calc_sharpe_ratio_sym(data,symbol,lookbackDays,enddate=dt.today(),index=None,silent=False):
  #data: Dataframe containing at least date for the required time period for the required symbol and index
  #symbol: Symbol for which sharpe ratio is to be calculated
  #lookbackDays: # of days to look back from the enddate to calculate sharpe ratio
  #enddate: Last day for sharpe ratio calculation
  #index: Reference index to be used
  #silent: silence print statements
  if index == None:
    index = getdata.getIndexTicker(getdata.getData([symbol],getdata.getParamDict('stock exchange')))
  #data = getdata.get_history([symbol,index],dt.today()-relativedelta(days=days))
  #data = data.drop(['Open','High','Low','Close','Volume'],axis=1)
  #data = data.unstack(0).swaplevel(0,1,axis=1).sortlevel(0,axis=1)
  data = append_return(data)
  r_sym = data.ix[symbol]['return'].ix[(enddate-relativedelta(days=lookbackDays)):enddate]
  r_index = data.ix[index]['return'].ix[(enddate-relativedelta(days=lookbackDays)):enddate]
  r_sym_mean = r_sym.mean()
  r_index_mean = r_index.mean()
  std_sym_wrt_index = (r_sym-r_index).std()
  answer = (r_sym_mean-r_index_mean)/std_sym_wrt_index
  if not silent:
    print days, "day Sharpe Ratio for",symbol, "=",answer
  return answer

def calc_sharpe_ratio_pf(data,portfolio,lookbackDays,enddate=dt.today(),index='^GSPC',silent=False):
  #data: Dataframe containing at least date for the required time period for all stocks in portfoilo and index
  #portfolio: Portfolio object for which sharpe ratio is to be calculated
  #lookbackDays: # of days to look back from the enddate to calculate sharpe ratio
  #enddate: Last day for sharpe ratio calculation
  #index: Reference index to be used
  #silent: silence print statements
  
  #tickers = portfolio.getTickersInPortfolio()
  #tickers.append(index)
  #data = getdata.get_history(tickers,dt.today()-relativedelta(days=days))
  #data = data.drop(['Open','High','Low','Close','Volume'],axis=1)
  data = data.unstack(0).swaplevel(0,1,axis=1).sortlevel(0,axis=1)
  data['PF','Adj Close'] = np.zeros(len(data))
  for stock in portfolio.getStocksInPortfolio():
    data['PF','Adj Close'] += data[stock.ticker,'Adj Close'] * stock.getSharesOwned()
    #data = data.drop(stock.ticker,axis=1,level=0)
  data = data.stack(0).swaplevel(0,1,axis=0).sortlevel(0,axis=0)
  data = append_return(data)
  r_sym = data.ix['PF']['return'].ix[(enddate-relativedelta(days=lookbackDays)):enddate]
  r_index = data.ix[index]['return'].ix[(enddate-relativedelta(days=lookbackDays)):enddate]
  r_sym_mean = r_sym.mean()
  r_index_mean = r_index.mean()
  std_sym_wrt_index = (r_sym-r_index).std()
  answer = (r_sym_mean-r_index_mean)/std_sym_wrt_index
  if not silent:
    print days, "day Sharpe Ratio for portfolio",portfolio.name,"=",answer
  return answer

def append_return(data):
  #helper function to append %return column to the dataframe
  data['return'] = np.zeros(len(data))
  for symbol in data.index.levels[0]:
    data.ix[symbol]['return'] = (data.ix[symbol]['Adj Close'] - data.ix[symbol]['Adj Close'].shift(1))/data.ix[symbol]['Adj Close']
  return data

def get_up_days(data):
  #helper function to filter only updays from dataframe
  return data[data['Open'] < data['Close']]

def get_down_days(data):
  #helper function to filer only down days from dataframe
  return data[data['Open'] > data['Close']]
  
def calc_RSI(data,symbol,lookbackDays,enddate=dt.today(),silent=False):
  #calculates relative strength index.
  #data: Dataframe containing at least date for the required time period for the required symbol
  #symbol: Symbol for which RSI is to be calculated
  #lookbackDays: # of days to look back from the enddate to calculate RSI
  #enddate: Last day for RSI
  #silent: silence print statements
  
  #data = getdata.get_history([symbol],dt.today()-relativedelta(days=days))
  data = data.ix[symbol].ix[(enddate-relativedelta(days=lookbackDays)):enddate]
  upDays = get_up_days(data)
  downDays = get_down_days(data)
  upAverage = (upDays['Close']-upDays['Open']).mean()
  downAverage = (downDays['Open']-downDays['Close']).mean()
  rs = upAverage/downAverage
  rsi = 100 - (100/(1+rs))
  if not silent:
    print days, "day RSI for",symbol,"=",rsi
    if rsi > 70:
      print "stock may be overbought."
    elif rsi < 30:
      print "stock may be oversold."
  return rsi

def look_for_RSI_divergence(data,symbol,days,silent=False):
##  A bullish divergence occurs when the underlying security
##  makes a lower low and RSI forms a higher low. RSI does not
##  confirm the lower low and this shows strengthening momentum.
##  A bearish divergence forms when the security records a
##  higher high and RSI forms a lower high. RSI does not
##  confirm the new high and this shows weakening momentum.
##  Before getting too excited about divergences as great trading
##  signals, it must be noted that divergences are misleading in a
##  strong trend. A strong uptrend can show numerous bearish divergences
##  before a top actually materializes. Conversely, bullish divergences
##  can appear in a strong downtrend - and yet the downtrend continues.
  pass