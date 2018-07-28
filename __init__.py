import os
import numpy as np
import pandas as pd
import talib
import statsmodels.api as sm

class my_data:
    '''
    The data used is stored in this class
    '''
    def __init__(self):
        '''
        The prices are read from csv files
        '''
        #close prices are read from a file
        self.close = pd.read_csv('close_prices.csv', index_col=0, 
                                 parse_dates=True, dayfirst=True)
        self.close = self.close.resample('D').fillna(method='ffill')
        #high prices are read from a file
        self.high = pd.read_csv('high_prices.csv', index_col=0, 
                                parse_dates=True, dayfirst=True)
        self.high = self.high.resample('D').fillna(method='ffill')
        #low prices are read from a file
        self.low = pd.read_csv('low_prices.csv', index_col=0, 
                               parse_dates=True, dayfirst=True)
        self.low = self.low.resample('D').fillna(method='ffill')
        #returns are caclulated
        self.returns = self.close.pct_change()
        
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
        #stores regimes
        self.regimes = None
        
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
    
    def generate_regimes(self, symbol):
        '''
        This function generates regimes based on Var and
        Triangular MA and ATR
        '''
        print ('Generating Regimes')
        close = db.close['S&P 500']
        close = pd.Series(talib.EMA(close.as_matrix(), 5), 
                          index = close.index)
        close =  close[close.index >= pd.to_datetime('01-01-2000')]
        high = db.high['S&P 500']
        low = db.low['S&P 500']
        high =  high.loc[close.index].fillna(method='ffill')
        low =  low.loc[close.index].fillna(method='ffill')
        returns = close.resample('W').first().pct_change().dropna()
        #Markov Autoregression model is fit for variance regimes
        mod_var_switch = sm.tsa.MarkovRegression(returns, k_regimes=2, 
                                                 trend='nc', 
                                                 switching_variance=True)
        res_var_switch = mod_var_switch.fit()
        var_regime = pd.DataFrame()
        var_regime['Price'] = close
        var_regime['var1'] = res_var_switch.smoothed_marginal_probabilities[0]
        var_regime['var1'].fillna(method='ffill', inplace=True)
        var_regime['var2'] = res_var_switch.smoothed_marginal_probabilities[1]
        var_regime['var2'].fillna(method='ffill', inplace=True)
        def regime(r):
            if r.var1 >= r.var2:
                return 'low var'
            return 'high var'
            if r.var2 > r.var1 and r.var2 > r.var3 and r.var2 > r.var4:
                return 2
            if r.var3 > r.var1 and r.var3 > r.var2 and r.var3 > r.var4:
                return 3
            return 4
        var_regime['var_regime_type'] = var_regime.apply(lambda r: regime(r), 
                  axis=1)
        #MA regimes are calculated using triangular MA and ATR
        ema_regime = pd.DataFrame()
        ema_regime['Price'] = close
        ema_regime['ema200'] = talib.TRIMA(close.as_matrix(),250)
        ema_regime['ATR'] = talib.ATR(high.as_matrix(),low.as_matrix(), 
                  close.as_matrix(),14)
        def ema_reg(r):
            if r.Price > r.ema200:
                if r.ATR is not None:
                    if r.Price > r.ema200 + r.ATR:
                        return 1
                    return 0
                return 1
            else:
                if r.ATR is not None:
                    if r.Price < r.ema200 - r.ATR:
                        return 0
                    return 1
                return 0
        ema_regime['ema_regime'] = ema_regime['Price'] > ema_regime['ema200']
        
        for i in range(len(ema_regime.index)):
            if i > 0:
                current_reg = ema_regime.loc[ema_regime.index[i], 'ema_regime']
                current_px = ema_regime.loc[ema_regime.index[i], 'Price']
                current_ema = ema_regime.loc[ema_regime.index[i], 'ema200']
                current_atr = ema_regime.loc[ema_regime.index[i], 'ATR']
                prev_reg = ema_regime.loc[ema_regime.index[i-1], 'ema_regime']
                if current_reg == 1 and prev_reg == 0:
                    if current_px < current_ema + 0.5*current_atr:
                        ema_regime.loc[ema_regime.index[i], 'ema_regime'] = 0
                if current_reg == 0 and prev_reg == 1:
                    if current_px > current_ema - 0.0*current_atr:
                        ema_regime.loc[ema_regime.index[i], 'ema_regime'] = 1
        
        ema_regime['ema_regime'] =\
        ema_regime.apply(lambda r: 'bullish' if r.ema_regime else 'bearish', 
                         axis=1)
        #Regimes are stored
        self.regimes =  pd.DataFrame()
        self.regimes['var_regime'] = var_regime['var_regime_type']
        self.regimes['ema_regime'] = ema_regime['ema_regime']
        self.regimes['regime_type'] = \
        self.regimes.apply(lambda r: r['ema_regime']+' + '+r['var_regime'], 
                           axis=1)
        print ('Generated Regimes')
        
class backtest_params:
    '''
    This class stores the backtest params
    '''
    def __init__(self):
        '''
        The values can be changed using here
        '''
        self.holding_period = 10000
        self.per_symbol_investment = 50000
        #transaction cost
        self.transaction_cost = 0.0001
        self.commission = 0.0001
        self.slippage = 0.0001
        #maximum investment per symbol
        self.max_inv_per_sym = 5
        #max holdng period
        self.max_holding_period= np.inf
        #use trailing stop loss
        self.trailing_stop_loss = 1
        #stop loss
        self.stop_loss = -np.inf
        #maximum profit
        self.max_profit = np.inf
        #define pyramid scheme
        self.pyramid = 'NONE'
        #define position sizing
        self.position_sizing = 'EQUAL'

class date_storage:
    '''
    This class handles the dates
    '''
    def __init__(self):
        self.current_date = None
        self.prev_date = None

#The data, params and date are stored as global variables           
db = my_data()
params = backtest_params()
date = date_storage()