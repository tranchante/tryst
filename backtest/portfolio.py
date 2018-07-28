# -*- coding: utf-8 -*-
from tryst.backtest.trade import *
import pandas as pd
import numpy as np
from datetime import timedelta
import tryst as bt

class MyPortfolio():
    """
    The portfolio class
    """
    def __init__(self, start_date=None, end_date=None):
        """
        Initialize the Porfolio class
        """
        #a list of active trades is stored
        self.trades_store = {}

        self._start_date = start_date
        self._end_date = end_date
        #store daily details of the portfolio
        self._daily_df = pd.DataFrame(columns=['long_value','short_value', 
                                               'stock_value', 'hedge_value',
                                               'pl_long', 'pl_short',
                                               'pl_stock', 
                                               'pl_hedge','pl_total'])
        #stats of portfolio  tracked
        self.max_consecutive_loss = 0
        self.consecutive_loss = 0
        self.gain = 0
        self.pain = 0
        self.positive_trades = 0
        self.total_trades = 0
        self.prev_trade = None
        self.cash = self.starting_cash = 1000000
        self.per_symbol_alloc = 1.0
        
    def initiate_trade(self, symbol, hedge_symbol, direction):
        '''
        initiate a trade with symbol, hedge and direction
        '''
        id = symbol+direction
        self.trades_store[id] = Trade(symbol, hedge_symbol, direction)
        self.trades_store[id].initiate_trade(self.cash*self.per_symbol_alloc)
        self.cash -= self.trades_store[id]._current_value
            
    def get_current_value(self):
        '''
        record the current value of portfolio and stocks
        and check constrints to mark trades to close
        '''        
        self._daily_df.loc[bt.date.current_date, 'long_value'] = 0
        self._daily_df.loc[bt.date.current_date, 'short_value'] = 0
        self._daily_df.loc[bt.date.current_date, 'stock_value'] = 0
        self._daily_df.loc[bt.date.current_date, 'hedge_value'] = 0
        self._daily_df.loc[bt.date.current_date, 'pl_long'] = 0
        self._daily_df.loc[bt.date.current_date, 'pl_short'] = 0
        self._daily_df.loc[bt.date.current_date, 'pl_stock'] = 0
        self._daily_df.loc[bt.date.current_date, 'pl_hedge'] = 0
        self._daily_df.loc[bt.date.current_date, 'pl_total'] = 0
        
        for p in self.trades_store.keys():
            trade = self.trades_store[p]
            self._daily_df.loc[bt.date.current_date,
                               'long_value'] += trade._long_value
            self._daily_df.loc[bt.date.current_date,
                               'short_value'] += trade._short_value
            self._daily_df.loc[bt.date.current_date,
                               'stock_value'] += trade._current_value
            self._daily_df.loc[bt.date.current_date,
                               'hedge_value'] += trade._hedge_current_value
            trade.update_value()
            self._daily_df.loc[bt.date.current_date,
                               'pl_long'] += trade._long_pl
            self._daily_df.loc[bt.date.current_date,
                               'pl_short'] += trade._short_pl
            self._daily_df.loc[bt.date.current_date,
                               'pl_stock'] += trade._current_pl
            self._daily_df.loc[bt.date.current_date,
                               'pl_hedge'] += trade._hedge_current_pl
            self._daily_df.loc[bt.date.current_date,
                               'pl_total'] += trade._current_pl+\
                               trade._hedge_current_pl                   
            self.trades_store[p].check_constraints()

    def close_trades(self):
        '''
        close trades that were marked for closing
        '''
        self._remove_list = []

        for p in self.trades_store.keys():
            trade = self.trades_store[p]
            self.track_stats(trade)
            if trade._to_close or bt.date.current_date == self._end_date:
                self._remove_list.append(p)
                self.cash += trade._current_value
                bt.db.add_costs(trade._current_value, 
                                trade._hedge_current_value, trade._direction, 
                                bt.date.current_date)
        for r in self._remove_list:
            self.trades_store.pop(r)

    def close_all_trades(self):
        '''
        close all trades 
        '''
        self._remove_list = []
        for p in self.trades_store.keys():
            trade = self.trades_store[p]
            self.track_stats(trade)
            self._remove_list.append(p)
            self.cash += trade._current_value
            bt.db.add_costs(trade._current_value, trade._hedge_current_value, 
                            trade._direction, bt.date.current_date)
        for r in self._remove_list:
            self.trades_store.pop(r)
        
            
    def add_returns(self):
        '''
        add cuumlative pl and returns to the daily data frame
        '''
        self.TC = bt.db.TC
        self.TC['total_cost'] = self.TC['long']+self.TC['short']  
        self.TC['cum_cost'] = self.TC['total_cost'].cumsum()
        self.commission = bt.db.commission
        self.commission['total_cost'] = self.commission['long']+self.commission['short']
        self.commission['cum_cost'] = self.commission['total_cost'].cumsum()
        self.slippage = bt.db.slippage
        self.slippage['total_cost'] = self.slippage['long']+self.slippage['short']
        self.slippage['cum_cost'] = self.slippage['total_cost'].cumsum()
        self._daily_df.loc[:, 'pl_stock'] -= bt.db.TC.loc[:, 'stock'] + \
        bt.db.commission.loc[:, 'stock'] + bt.db.slippage.loc[:, 'stock']
        self._daily_df.loc[:, 'pl_hedge'] -= bt.db.TC.loc[:, 'hedge'] + \
        bt.db.commission.loc[:, 'hedge'] + bt.db.slippage.loc[:, 'hedge']
        self._daily_df.loc[:, 'pl_long'] -= bt.db.TC.loc[:, 'long'] + \
        bt.db.commission.loc[:, 'long'] + bt.db.slippage.loc[:, 'long']
        self._daily_df.loc[:, 'pl_short'] -= bt.db.TC.loc[:, 'short'] +\
        bt.db.commission.loc[:, 'short'] + bt.db.slippage.loc[:, 'short']
        self._daily_df.loc[:, 'pl_total'] = self._daily_df.loc[:, 'pl_stock']+\
        self._daily_df.loc[:, 'pl_hedge']
        self._daily_df.loc[:, 'cum_pl'] = self._daily_df.loc[:, 
                          'pl_total'].cumsum()
        self._daily_df.loc[:, 'cum_pl_stock'] = self._daily_df.loc[:, 
                          'pl_stock'].cumsum()
        self._daily_df.loc[:, 'cum_pl_hedge'] = self._daily_df.loc[:, 
                          'pl_hedge'].cumsum()
        self._daily_df['gross_exposure'] = self._daily_df['stock_value'] +\
        self._daily_df['hedge_value']
        
        def total_return(r):
            if r['gross_exposure'] == 0:
                return None
            return r['pl_total'] / r['gross_exposure']
        self._daily_df.loc[:, 
                           'return_total'] =\
                           self._daily_df.apply(lambda r: total_return(r), 
                                                axis=1)
            
    def track_stats(self, trade):
        """
        upon closing a trade we record the PL and
        other records related to trades
        """
        total_pl = trade._current_value + trade._hedge_current_value -\
        trade._entry_value - trade._hedge_entry_value
        #track max consecutive loss and pain
        if total_pl < 0:
            if self.prev_trade is None or self.prev_trade == 'loss':
                self.consecutive_loss += 1
            else:
                self.consecutive_loss = 1
            self.max_consecutive_loss = max(
                self.consecutive_loss, self.max_consecutive_loss)
            self.pain += total_pl
            self.prev_trade = 'loss'
        #track gain and positive trades
        elif total_pl > 0:
            self.positive_trades += 1
            self.gain += total_pl
            self.prev_trade = 'profit'
        self.total_trades += 1