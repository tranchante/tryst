# -*- coding: utf-8 -*-
from backtester.backtest.portfolio import *
import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
import backtester as bt
plt.style.use('seaborn')

class MyBacktest():
    """
    The backtest class
    """
    def __init__(self, start_date, end_date):
        '''
        Initialize the class
        '''
        self._start_date = start_date
        self._end_date = end_date
        self._portfolio = MyPortfolio(self._start_date, self._end_date)
        #model fitted per stock
        self.models = {}
        #holding period declared
        self.holding_period = bt.params.holding_period
        #model trained per 100 days
        self.prices = bt.db.close
        self.returns = bt.db.returns
        self.name = ''

    def rebalance(self):
        '''
        rebalance the portfolio based on model predictions
        '''      
        pass
    
    def backtest(self):
        '''
        iterate through the days and implement the backtest
        '''
        bt.date.current_date = self._start_date
        
        while bt.date.current_date <= self._end_date:
            if bt.date.current_date.weekday() <= 4:
                bt.db.TC.loc[bt.date.current_date, :] = np.zeros((6))
                bt.db.commission.loc[bt.date.current_date, :] = np.zeros((6))
                bt.db.slippage.loc[bt.date.current_date, :] = np.zeros((6))
                self._portfolio.get_current_value()
                self.rebalance()
                self._portfolio.close_trades()
            bt.date.prev_date = bt.date.current_date
            bt.date.current_date += timedelta(days=1)
            days = (bt.date.current_date - self._start_date).days
            if days%365 == 0:
                print ('Strategy run for {} year'.format(int(days/365)))
        self._portfolio.add_returns()
        
    def analyse(self, regime=None):
        '''
        analyse the results of the backtest
        '''
        df = self._portfolio._daily_df
        portfolio_size = self._portfolio.starting_cash
        # total number of trades
        num_trades = self._portfolio.total_trades
        # positive trades
        positive_trades = self._portfolio.positive_trades
        #profit loss ratio
        if positive_trades > 0:
            PLR = (self._portfolio.gain / positive_trades)
        else:
            PLR = 0
        PLR /= abs(self._portfolio.pain / (num_trades - positive_trades))
        p = positive_trades / num_trades
        # wining percentage
        win_perc = positive_trades / num_trades
        # win to loss ratio
        if num_trades - positive_trades > 0:
            winloss = positive_trades / (num_trades - positive_trades)
        else:
            winloss = np.inf
        # return per trade
        pl_mean = df.pl_total.mean()
        pl_std = df.pl_total.std()
        # calculate Max consecutive loss
        max_cons_loss = self._portfolio.max_consecutive_loss
        # calaulte max drawdown
        s = df.cum_pl + portfolio_size
        drawdown = 1 - s / s.cummax()
        mdd = -1 * drawdown.max()
        # calculate CAGR - annualize average daily return
        periods = (df.index[-1] - df.index[0]).days / 365
        last = df.loc[df.index[-1], 'cum_pl'] + portfolio_size
        first = portfolio_size
        cagr = (last / first)**(1 / periods) - 1
        vol = np.std(self._portfolio._daily_df['return_total'].dropna())
        # calculate lake ratio
        p = s.cummax()
        water = sum(p - s)
        earth = sum(s)
        lake_ratio = water / earth
        # calculate gain to pain ratio
        if self._portfolio.pain != 0:
            gain_to_pain = self._portfolio.gain / abs(self._portfolio.pain)
        else:
            gain_to_pain = np.inf
        # tabulate reults
        output = pd.DataFrame(columns=['value'])
        output.loc['CAGR %', 'value'] = cagr * 100
        output.loc['Annualized Risk %', 'value'] = vol * np.sqrt(252)*100
        output.loc['Sharpe %', 'value'] = 100*cagr/(vol*np.sqrt(252))
        
        output.loc['Win %', 'value'] = win_perc * 100
        output.loc['Num Trades', 'value'] = num_trades
        output.loc['Win to Loss Ratio', 'value'] = winloss
        output.loc['Average Daily PL $', 'value'] = pl_mean
        output.loc['Average Daily Std $', 'value'] = pl_std
        
        daily_ret = np.mean(self._portfolio._daily_df['return_total'].dropna())
        output.loc['Daily Return bps (total)', 'value'] = daily_ret * 10000
        output.loc['Max Consecutive Losers', 'value'] = max_cons_loss
        output.loc['Max Drawdown %', 'value'] = mdd * 100
        output.loc['Lake Ratio', 'value'] = lake_ratio
        output.loc['Gain to Pain Ratio', 'value'] = gain_to_pain
        print (output)
        output.to_csv(self.name+'_output.csv')
        self._portfolio._daily_df.to_csv(self.name+'_daily_df.csv')
        #plot the PL
        plt.figure(figsize=[10, 12])
        ax = plt.subplot2grid((7, 1), (0, 0), rowspan=5)
        plt.title('PL chart')
        df = pd.DataFrame()
        df['regime'] = bt.db.regimes.regime_type
        df['pl'] = self._portfolio._daily_df.cum_pl
        df['ret'] = self._portfolio._daily_df.return_total
        df['bearish + low var'] = df.apply(lambda r: r['pl'] if \
          r.regime =='bearish + low var' else None, axis=1 )
        df['bullish + low var'] = df.apply(lambda r: r['pl'] if \
          r.regime =='bullish + low var' else None, axis=1 )
        df['bearish + high var'] = df.apply(lambda r: r['pl'] if \
          r.regime =='bearish + high var' else None, axis=1 )
        df['bullish + high var'] = df.apply(lambda r: r['pl'] if\
          r.regime =='bullish + high var' else None, axis=1 )
        
        if regime is None or regime == 'bearish + low var':
            df['bearish + low var'].plot(ax=ax)
        if regime is None or regime == 'bullish + low var':    
            df['bullish + low var'].plot(ax=ax)
        if regime is None or regime == 'bearish + high var':
            df['bearish + high var'].plot(ax=ax)
        if regime is None or regime == 'bullish + high var':
            df['bullish + high var'].plot(ax=ax)
        plt.legend()
        ax = plt.subplot2grid((7, 1), (5, 0), rowspan=1)
        plt.title('Transaction Cost chart')
        costs = self._portfolio.TC.cum_cost +\
                self._portfolio.slippage.cum_cost +\
                self._portfolio.commission.cum_cost
        costs.plot(color='g', label = 'total pl', ax=ax)
        ax = plt.subplot2grid((7, 1), (6, 0), rowspan=2)
        plt.title('Mean Return per Regime')
        df.groupby('regime').mean()['ret'].plot(kind='bar', ax=ax)
        plt.xticks(rotation=45)
        print (df.groupby('regime').mean()['ret'])
        plt.tight_layout()
        plt.savefig(self.name+'_chart.png')
        return output
        
    @property
    def current_date(self):
        return bt.date.current_date
    
    @property
    def prev_date(self):
        return bt.date.prev_date