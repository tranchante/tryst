# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 22:43:58 2017

@author: Sonam Srivastava
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
from math import ceil
from lxml import etree
import pickle
import pandas as pd
import good_morning as gm
import os
import tryst.data.quandl as download

class my_data:
    '''
    The data used is stored in this class
    '''            
    def __init__(self):
        path =  os.path.dirname(os.path.abspath(download.__file__))
        print ('data stored at', path)
        self.symbols = pickle.load(open(os.path.join(path, 'my_symbols.p'), 'rb'))
        self.db = os.path.join(path, 'db.h5')
        self.start_date = pd.to_datetime('01-01-2000')
        self.end_date = pd.to_datetime('01-01-2018')
        self.open = pd.read_hdf(self.db, 'open').resample('D').ffill().fillna(method='pad').fillna(method='bfill')
        self.high = pd.read_hdf(self.db, 'high').resample('D').ffill().fillna(method='pad').fillna(method='bfill')
        self.low = pd.read_hdf(self.db, 'low').resample('D').ffill().fillna(method='pad').fillna(method='bfill')
        self.close = pd.read_hdf(self.db, 'close').resample('D').ffill().fillna(method='pad').fillna(method='bfill')
        self.volume = pd.read_hdf(self.db, 'volume').resample('D').ffill().fillna(method='pad').fillna(method='bfill')
        self.returns = self.close.pct_change().fillna(0).resample('D').ffill().fillna(method='pad').fillna(method='bfill')
        self.repurchase_price = pd.read_hdf(self.db, 'repurchase_price').resample('D').ffill().fillna(method='pad').fillna(method='bfill')
        self.sale_price = pd.read_hdf(self.db, 'sale_price').resample('D').ffill().fillna(method='pad').fillna(method='bfill')
        self.nav = pd.read_hdf(self.db, 'nav').resample('D').ffill().fillna(method='pad').fillna(method='bfill')
                #stores transaction costs        
        self.TC = pd.DataFrame(columns=['long', 'short', 'stock', 
                                        'hedge', 'total_cost', 'cum_cost'])
        #stores commissions
        self.commission = pd.DataFrame(columns=['long', 'short', 'stock', 
                                                'hedge', 'total_cost', 
                                                'cum_cost'])
        #store slippage
        self.slippage = pd.DataFrame(columns=['long', 'short', 'stock', 
                                              'hedge', 'total_cost', 
                                              'cum_cost'])

    def add_costs(self, value, hedge_value, direction, date):
        '''
        Costs are added using this function for each trade
        using the costs defined in params
        '''
        self.TC.loc[date, 'stock'] += value*params.transaction_cost
        self.TC.loc[date, 'hedge'] += hedge_value*params.transaction_cost
        if direction == 'LONG':
            self.TC.loc[date, 'long'] += value*params.transaction_cost 
            self.TC.loc[date, 'short'] += hedge_value*params.transaction_cost 
        else:
            self.TC.loc[date, 'short'] += value*params.transaction_cost 
            self.TC.loc[date, 'long'] += hedge_value*params.transaction_cost 
        self.commission.loc[date, 'stock'] += value*params.commission
        self.commission.loc[date, 'hedge'] += hedge_value*params.commission
        if direction == 'LONG':
            self.commission.loc[date, 'long'] += value*params.commission 
            self.commission.loc[date, 'short'] += hedge_value*params.commission 
        else:
            self.commission.loc[date, 'short'] += value*params.commission 
            self.commission.loc[date, 'long'] += hedge_value*params.commission 
        self.slippage.loc[date, 'stock'] += value*params.slippage
        self.slippage.loc[date, 'hedge'] += hedge_value*params.slippage
        if direction == 'LONG':
            self.slippage.loc[date, 'long'] += value*params.slippage 
            self.slippage.loc[date, 'short'] += hedge_value*params.slippage 
        else:
            self.slippage.loc[date, 'short'] += value*params.slippage 
            self.slippage.loc[date, 'long'] += hedge_value*params.slippage 
            
    def create_db(self):
        for s in self.symbols:
            if s in self.open.columns: continue
            if s in self.nav.columns: continue
            data = download.get_daily_data(s, self.start_date, self.end_date)
            print (s)
            if data is not None:
                if 'Open' in data.columns:
                    self.open[s] = data['Open']
                    self.high[s] = data['High']
                    self.low[s] = data['Low']
                    self.close[s] = data['Close']
                    if 'Shares Traded' in data.columns:
                        self.volume[s] = data['Shares Traded']
                    if 'Total Traded Quantity' in data.columns:
                        self.volume[s] = data['Total Traded Quantity']
                else:
                    if 'Value' in data.columns:
                        self.close[s] = data['Value']
                    elif 'Repurchase Price' in data.columns:
                        self.repurchase_price[s] = data['Repurchase Price']
                        self.sale_price[s] = data['Sale Price']
                        self.nav[s] = data['Net Asset Value']
        self.save()
        
    def save(self):
        self.open.to_hdf(self.db, 'open')
        self.high.to_hdf(self.db, 'high')
        self.low.to_hdf(self.db, 'low')
        self.close.to_hdf(self.db, 'close')
        self.volume.to_hdf(self.db, 'volume')
        self.repurchase_price.to_hdf(self.db, 'repurchase_price')
        self.sale_price.to_hdf(self.db, 'sale_price')
        self.nav.to_hdf(self.db, 'nav')
    
    def update_db(self):
        start_date = max(self.close.index)
        end_date = datetime.datetime.now()
        open_ = pd.DataFrame()
        high = pd.DataFrame()
        low = pd.DataFrame()
        close = pd.DataFrame()
        volume = pd.DataFrame()
        for s in self.symbols:
            data = download.get_daily_data(s, start_date, end_date)
            if data is not None:
                open_[s] = data['Open']
                high[s] = data['High']
                low[s] = data['Low']
                close[s] = data['Close']
                volume[s] = data['Shares Traded']
        self.open = pd.concat([self.open, open_])
        self.high = pd.concat([self.high, high])
        self.low = pd.concat([self.low, low])
        self.close = pd.concat([self.close, close])
        self.volume = pd.concat([self.volume, volume])
        self.save()
            
#def create_components_db():
#    '''
#    This function pushes the coponents of S&P 500 into a database named
#    SNP_COMPONENTS
#    '''
#    conn = sqlite3.connect('database.db')
#    df = obtain_parse_wiki_snp500()
#    df.to_sql("SNP_COMPONENTS", conn, if_exists="replace")
#    conn.commit()
#    conn.close()
#    print('created database of S&P 500 components')
#
#
#def create_daily_ohlc_db(num_years=5):
#    '''
#    This function downloads the daily OHLC for the coponents of S&P 500
#    and pushes it into a database named
#    DAILY_OHLC
#    '''
#    conn = sqlite3.connect('snp_database.db')
#    for symbol in get_components().ticker:
#        df = get_data_daily(symbol, num_years=num_years)
#        df['symbol'] = symbol
#        df.to_sql("DAILY_OHLC", conn, if_exists="append")
#        print('added daily OHLC for {} {}'.format(symbol, len(df)))
#    conn.close()
#
#
#def create_minbin_ohlc_db(num_days=20):
#    '''
#    This function downloads the minute binned OHLC for the coponents of S&P 500
#    and pushes it into a database named
#    MINBIN_OHLC
#    '''
#    conn = sqlite3.connect('snp_database.db')
#    for symbol in get_components().ticker:
#        df = get_data_minutebinned(symbol, num_days=20)
#        df['symbol'] = symbol
#        df.to_sql("MINBIN_OHLC", conn, if_exists="append")
#        print('added minute binned OHLC for {}'.format(symbol))
#    conn.close()
#
#
#def download_fundamentals(symbol='AAPL'):
#    '''
#    This function downloads the fundamental data for the coponents of S&P 500
#    from morningstar API and pushes it into separate databases called
#    CASH_FLOW, BALANCE_SHEET and INCOME_STATEMENT
#    '''
#    conn = sqlite3.connect('snp_database.db')
#    kr = gm.FinancialsDownloader()
#    kr_frames = kr.download('AAPL')
#    cash_flow = kr_frames['cash_flow'].drop('parent_index', axis=1)
#    cash_flow['symbol'] = symbol
#    income_statement = kr_frames['income_statement'].drop(
#        'parent_index', axis=1)
#    income_statement['symbol'] = symbol
#    balance_sheet = kr_frames['balance_sheet'].drop('parent_index', axis=1)
#    balance_sheet['symbol'] = symbol
#    cash_flow.to_sql("CASH_FLOW", conn, if_exists="append")
#    income_statement.to_sql("INCOME_STATEMENT", conn, if_exists="append")
#    balance_sheet.to_sql("BALANCE_SHEET", conn, if_exists="append")
#    conn.close()
#    print('added fundamentals for {}'.format(symbol))
#
#
#def create_fundamentals_db():
#    '''
#    This function updates the fundamentaldb for all stocks
#    '''
#    for symbol in get_components().ticker:
#        download_fundamentals(symbol)
#
#
#def get_components():
#    '''
#    This function queries the SNP_COMPONETS and returns all components
#    '''
#    conn = sqlite3.connect('snp_database.db')
#    df = pd.read_sql_query("SELECT * FROM SNP_COMPONENTS", conn)
#    conn.close()
#    return df
#
#
#def get_daily_ohlc(symbol):
#    '''
#    This function queries the DAILY_OHLC to get daily OHLC for a symbol
#    '''
#    conn = sqlite3.connect('snp_database.db')
#    df = pd.read_sql_query(
#        'select * from DAILY_OHLC where symbol=\'{}\''.format(symbol), conn)
#    conn.close()
#    return df
#
#
#def get_minbin_ohlc(symbol):
#    '''
#    This function queries the MINBIN_OHLC to get minute binned OHLC 
#    for a symbol
#    '''
#    conn = sqlite3.connect('snp_database.db')
#    df = pd.read_sql_query(
#        'select * from MINBIN_OHLC where symbol=\'{}\''.format(symbol), conn)
#    conn.close()
#    return df
#
#
#def get_cashflow(symbol):
#    '''
#    This function queries the CASH_FLOW to cash flow data for a symbol
#    '''
#    conn = sqlite3.connect('snp_database.db')
#    df = pd.read_sql_query(
#        'select * from CASH_FLOW where symbol=\'{}\''.format(symbol), conn)
#    conn.close()
#    return df
#
#
#def get_balancesheet(symbol):
#    '''
#    This function queries the BALANCE_SHEET to balance sheet data for a symbol
#    '''
#    conn = sqlite3.connect('snp_database.db')
#    df = pd.read_sql_query(
#        'select * from BALANCE_SHEET where symbol=\'{}\''.format(symbol), conn)
#    conn.close()
#    return df
#
#
#def get_incomestatement(symbol):
#    '''
#    This function queries the INCOME_STATEMENT to income statement data 
#    for a symbol
#    '''
#    conn = sqlite3.connect('snp_database.db')
#    df = pd.read_sql_query(
#        'select * from INCOME_STATEMENT where symbol=\'{}\''.format(symbol), conn)
#    conn.close()
#    return df
#
#
#if __name__ == '__main__':
#    d = my_data()
#    d.create_db()
##    create_components_db()
##    create_daily_ohlc_db(num_years=25)
##    create_minbin_ohlc_db(num_days=20)
##    create_fundamentals_db()
##    print(get_daily_ohlc('AAPL'))
##    print(get_minbin_ohlc('AAPL'))
##    print(get_cashflow('AAPL'))
##    print(get_balancesheet('AAPL'))
##    print(get_incomestatement('AAPL'))
