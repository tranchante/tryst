# -*- coding: utf-8 -*-
"""
Created on Mon Jan  1 00:59:12 2018

@author: sonaa
"""
import numpy as np
class backtest_params:
    def __init__(self):
        self.holding_period = 20
        self.per_symbol_investment = 50000
        #transaction cost
        self.transaction_cost = 0.0003
        #maximum investment per symbol
        self.max_inv_per_sym = 5
        #max holdng period
        self.max_holding_period= np.inf
        #use trailing stop loss
        self.trailing_stop_loss = True
        #stop loss
        self.stop_loss = -0.05
        #maximum profit
        self.max_profit = np.inf
        #define pyramid scheme
        self.pyramid = 'EQUAL'
        #define position sizing
        self.position_sizing = 'EQUAL'
        