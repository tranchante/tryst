# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import timedelta
import tryst as bt

class Trade():
    '''
    The single Trade Class
    '''

    def __init__(self, symbol, hedge_symbol, direction):
        '''
        Initialize the Trade trade Class
        '''
        self._entry_date = None

        self._shares = 0
        self._current_value = 0.0
        self._entry_price = 0.0
        self._entry_value = 0.0

        self._hedge_shares = 0
        self._hedge_current_value = 0.0
        self._hedge_entry_price = 0.0
        self._hedge_entry_value = 0.0
        self._current_pl = 0.0
        self._hedge_current_pl = 0.0

        self._max_port_value = 0

        self._to_close = 0
        self._reason = None
        self.increase_investment = False
        self.incremental_entry_value = 0
        self.max_ever_value = 0
        self._stock_name = symbol
        self._hedge_name = hedge_symbol
        self._direction = direction
        self._hedge_direction = 'SELL' if direction == 'BUY' else 'BUY'
        #max investment per symbol
        self.per_symbol_investment = bt.params.per_symbol_investment
        #maximum investment per symbol
        self.max_inv_per_sym = bt.params.max_inv_per_sym
        #max holdng period
        self.max_holding_period= bt.params.max_holding_period
        #use trailing stop loss
        self.trailing_stop_loss = bt.params.trailing_stop_loss
        #stop loss
        self.stop_loss = bt.params.stop_loss
        #maximum profit
        self.max_profit = bt.params.max_profit
        #define pyramid scheme
        self.pyramid = bt.params.pyramid
        #define position sizing
        self.position_sizing = bt.params.position_sizing
        #track number of increases 
        self.num_increase = 0
        self.prices = bt.db.close
        self.returns = bt.db.returns
        
    def initiate_trade(self, value=None):
        '''
        Initiate the trade by setting entry price, value, shares etc
        '''
        self._entry_date = bt.date.current_date

        self._entry_price = self._current_price()

        self.max_ever_value = self.per_symbol_investment 
        if value is None:
            #if position sizing is equal - invest equal amounts per trade
            if self.position_sizing == 'EQUAL':
                self.single_entry_value = self.max_ever_value /\
                self.max_inv_per_sym
            #if position sizing is equal - invest value based on risk
            elif self.position_sizing == 'RISK ADJUSTED':
                self.single_entry_value = self.max_ever_value /\
                self.max_inv_per_sym/3/self._std()
            #if position sizing is equal - invest value based on kelly value
            elif self.position_sizing == 'KELLY':
                self.single_entry_value = self.kelly()*self.max_ever_value /\
                self.max_inv_per_sym
        else:
            self.single_entry_value = value
        #by pyramiding scheme upright - increase by half the previous investment
        if self.pyramid == 'UPRIGHT':            
            self.incremental_entry_value = 0.5*self.single_entry_value
        #by pyramiding scheme upright - increase by same value as the previous investment
        elif self.pyramid == 'EQUAL':
            self.incremental_entry_value = self.single_entry_value
        #by pyramiding scheme upright - increase by half the previous investment
        #initially and then decrease inestement
        elif self.pyramid == 'REFLECTIVE':
            self.incremental_entry_value = 0.5*self.single_entry_value
        else:
            self.incremental_entry_value = 0
        
        #calulate entry values
        self._entry_value = self._current_value = self.single_entry_value
        self._shares = self._current_value / self._entry_price
        self._entry_value = self._current_value
        
        #calculate hedge entry values
        if self._hedge_name is not None:
            self._hedge_entry_price = self._hedge_current_price()
            self._hedge_entry_price = self._hedge_entry_price
            self._hedge_current_value = self._current_value
            self._hedge_entry_value = self._hedge_current_value
            self._hedge_shares = self._hedge_current_value / \
            self._hedge_entry_price
        bt.db.add_costs(self._current_value, self._hedge_current_value, 
                        self._direction, bt.date.current_date)    
        self._max_port_value = self._current_value + self._hedge_current_value

    def kelly(self):
        '''
        if applying kelly criteria - get position size
        '''
        loc = self.prices.index.get_loc(bt.date.current_date)
        history = self.prices.loc[self.prices.index[loc-100:loc], self._stock_name]
        W = sum(history[history > 0])/(sum(history[history > 0])+\
                abs(sum(history[history < 0])))
        wl = len(history[history > 0])/len(history)
        if len(history) > 0 and wl > 0:
            k = W - ((1 - W) / wl)
            if np.isfinite(k) and k > 0:
                return k
        return 1

    def adjust_entry_values(
            self,
            new_price,
            new_hedge_price,
            add_shares,
            add_hedge_shares,
            add_value,
            add_hedge_value):
        '''
        adjust entry price/value for additions/deletions
        '''
        self._entry_price = (self._entry_price * self._shares +
                             new_price * add_shares) / \
                             (self._shares + add_shares)
        if self._hedge_shares + add_hedge_shares > 0:
            self._hedge_entry_price = (
                self._hedge_entry_price *
                self._shares + new_hedge_price * add_hedge_shares) / (
                self._hedge_shares + add_hedge_shares)
        self._current_value += add_value
        self._entry_value += add_value
        self._shares += add_shares
        if self._hedge_name is not None:
            self._hedge_current_value += add_hedge_value
            self._hedge_entry_value += add_hedge_value
            self._hedge_shares += add_hedge_shares
        bt.db.add_costs(add_value, add_hedge_value, self._direction,
                        bt.date.current_date)    
        self._max_port_value = self._current_value + self._hedge_current_value

    def increase_investment_fn(self):
        '''
        Increase Investment in the active trade
        '''
        if  self.pyramid == 'NONE': return
        new_price = self._current_price()
        new_hedge_price = self._hedge_current_price()
        
        self.incremental_entry_value = min(
            self.incremental_entry_value,
            self.max_ever_value - self._entry_value)
        
        add_value = self.incremental_entry_value
        add_shares = add_value / new_price
        if add_value <= 0:
            return
        
        if self._hedge_name is not None:
            add_hedge_value =  add_value
            add_hedge_shares = add_hedge_value / new_hedge_price
        else:
            add_hedge_value =  0
            add_hedge_shares = 0
        self.num_increase += 1
        self.adjust_entry_values(
            new_price,
            new_hedge_price,
            add_shares,
            add_hedge_shares,
            add_value,
            add_hedge_value)
        self.num_increase += 1
        
        #for upright pyramiding increase is half the previous investment
        if self.pyramid == 'UPRIGHT':            
            self.incremental_entry_value = 0.5*self.incremental_entry_value
        #for reflective pyramiding increase is half the previous investment
        #initially and then decrese investment
        elif self.pyramid == 'REFLECTIVE':
            if self.num_increase < 3:
                self.incremental_entry_value = 0.5*self.incremental_entry_value
            elif self.num_increase == 3:
                self.incremental_entry_value = -self.incremental_entry_value
            else:
                self.incremental_entry_value = 2*self.incremental_entry_value
            
    def check_constraints(self):
        '''
        check holding period, stop loss and max profit constraints
        '''
        if (bt.date.current_date - self._entry_date).days >= \
        self.max_holding_period:
            self._to_close = True
            print ('holdingperiod')
        else:
            if self.trailing_stop_loss:
                total_pl = self._current_value + self._hedge_current_value -\
                self ._max_port_value
                total_return = total_pl / (self._max_port_value)
            else:
                total_pl = self._current_value + self._hedge_current_value -\
                self._entry_value - self._hedge_entry_value
                total_return = total_pl /   (self._entry_value +\
                                             self._hedge_entry_value)
            if total_return <= self.stop_loss:
                self._to_close = True
                print ('stoploss')
            
            if total_return >= self.max_profit:
                self._to_close = True
                print ('maxprofit')

    def update_value(self):
        '''
        calculate current value and pl
        '''
        
        self._current_pl = self._current_value * self._current_return()
        self._hedge_current_pl = self._hedge_current_value *\
        self._hedge_current_return()
        self._current_value += self._current_pl
        self._hedge_current_value += self._hedge_current_pl
        
        if self._current_return() > self._std():
            self.increase_investment_fn()
        self._max_port_value = max(
            self._max_port_value,
            self._current_value +
            self._hedge_current_value)

    @property
    def _long_value(self):
        '''
        get long value
        '''
        long_value = 0
        if self._direction == 'BUY':
            long_value += self._current_value
        return long_value

    @property
    def _short_value(self):
        '''
        get short value
        '''
        short_value = 0
        if self._direction == 'SELL':
            short_value += self._current_value
        return short_value

    @property
    def _long_pl(self):
        '''
        get long pl
        '''
        long_pl = 0
        if self._direction == 'BUY':
            long_pl += self._current_pl
        return long_pl

    @property
    def _short_pl(self):
        '''
        get short pl
        '''
        short_pl = 0
        if self._direction == 'SELL':
            short_pl += self._current_pl
        return short_pl   


    @property
    def get_pl(self):
        '''
        get total pl
        '''
        return self._current_value + self._hedge_current_value - \
            self._entry_value - self._hedge_entry_value

    def _std(self):
        '''
        get vol
        '''
        loc = self.returns.index.get_loc(bt.date.current_date)
        return self.returns.loc[self.returns.index[loc-20:loc],\
                                self._stock_name].dropna().std()

    def _current_return(self):
        '''
        get current return
        '''
        sign = 1 if self._direction == 'BUY' else -1
        return sign*self.returns.loc[bt.date.current_date, self._stock_name]

    def _hedge_current_return(self): 
        '''
        get hedge current return
        '''
        if self._hedge_name is None:
            return 0
        sign = 1 if self._hedge_direction == 'BUY' else -1        
        return sign*self.returns.loc[bt.date.current_date, self._hedge_name]
            
    def _hedge_current_price(self):
        '''
        get hedge current adj price
        '''
        if self._hedge_name is None:
            return 0
        return self.prices.loc[bt.date.current_date, self._hedge_name]
    
    def _current_price(self):
        '''
        get current adj price
        '''       
        return self.prices.loc[bt.date.current_date, self._stock_name]
