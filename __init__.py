import os
import numpy as np
import pandas as pd
import talib
import statsmodels.api as sm
from tryst.data.db import my_data

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