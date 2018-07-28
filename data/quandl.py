# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 00:09:08 2017

@author: Sonam Srivastva
"""

import pandas as pd
import quandl
quandl.ApiConfig.api_key = "Vid3WpRjLpxyzzMBsFut"

def get_daily_data(symbol, start_date=None, end_date=None):
    try:
        if start_date is None or end_date is None or  type(start_date) is str or type(end_date) is str:
            return quandl.get(symbol)
        else:
            return quandl.get(symbol, start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
    except Exception as e: 
        print (e, symbol)
        return None

def get_data_daily(symbol, interval_seconds=24*3600, num_years=25):
    """
    This function downloads the data at given frequency (interval seconds)
    for a given nunber of years for a given symbol from Google Finance
    """
    df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
    symbol = symbol.upper()
    # First try to download the data for index
    url_string = "http://www.google.com/"
    url_string += "finance/getprices?q={0}".format(symbol)
    url_string += "&x=NYSE&p={0}Y&i={1}".format(num_years, interval_seconds)
    url_string += '&f=d,o,h,l,c,v'
    # Exception handling done to take care of http errors
    try:
        csv = urlrequest.urlopen(url_string).readlines()
        # first 6 lines of the file contain static information
        for bar in range(7, len(csv)):
            l = csv[bar].decode('utf8')
            if l.count(',') != 5:
                continue  # the ohlcv data has 5 elements
            offset, close, high, low, open_, volume = l.replace(
                '\n', '').split(',')
            if offset[0] == 'a':  # offsets with prefix a contain dates
                day = float(offset[1:])
                offset = 0
            else:
                # offset without prefix a contain offset
                offset = float(offset)
            open_, high, low, close = [float(x)
                                       for x in [open_, high, low, close]]
            # unix timestamp converted to datetime
            dt = datetime.fromtimestamp(day + (interval_seconds * offset))
            # dataframe populated
            df.loc[dt, :] = [open_, high, low, close, volume]
    except Exception as e:
        print(e)
    # If data not found then try to download the data for NASDAQ
    if len(df) == 0:
        url_string = "http://www.google.com/"
        url_string += "finance/getprices?q={0}".format(symbol)
        url_string += "&x=NASDAQ&p={0}Y&i={1}".format(
            num_years, interval_seconds)
        url_string += '&f=d,o,h,l,c,v'
        # Exception handling done to take care of http errors
        try:
            csv = urlrequest.urlopen(url_string).readlines()
            # first 6 lines of the file contain static information
            for bar in range(7, len(csv)):
                l = csv[bar].decode('utf8')
                if l.count(',') != 5:
                    continue  # the ohlcv data has 5 elements
                offset, close, high, low, open_, volume = l.replace(
                    '\n', '').split(',')
                if offset[0] == 'a':  # offsets with prefix a contain dates
                    day = float(offset[1:])
                    offset = 0
                else:  # offset without prefix a contain offset
                    offset = float(offset)
                open_, high, low, close = [
                    float(x) for x in [
                        open_, high, low, close]]
                # unix timestamp converted to datetime
                dt = datetime.fromtimestamp(day + (interval_seconds * offset))
                # dataframe populated
                df.loc[dt, :] = [open_, high, low, close, volume]
        except Exception as e:
            print(e)
    # If data not found then try to download the data for NYSE
    if len(df) == 0:
        url_string = "http://www.google.com/finance/getprices?q={0}".format(
            symbol)
        url_string += "&p={0}&i={1}Y".format(num_years, interval_seconds)
        url_string += "&f=d,o,h,l,c,v"
        # Exception handling done to take care of http errors
        try:
            csv = urlrequest.urlopen(url_string).readlines()
            # first 6 lines of the file contain static information
            for bar in range(7, len(csv)):
                l = csv[bar].decode('utf8')
                if l.count(',') != 5:
                    continue  # the ohlcv data has 5 elements
                offset, close, high, low, open_, volume = l.replace(
                    '\n', '').split(',')
                if offset[0] == 'a':  # offsets with prefix a contain dates
                    day = float(offset[1:])
                    offset = 0
                else:  # offset without prefix a contain offset
                    offset = float(offset)
                open_, high, low, close = [
                    float(x) for x in [
                        open_, high, low, close]]
                # unix timestamp converted to datetime
                dt = datetime.fromtimestamp(day + (interval_seconds * offset))
                # dataframe populated
                df.loc[dt, :] = [open_, high, low, close, volume]
        except Exception as e:
            print(e)
    # datafrane returned
    return df


def get_data_minutebinned(symbol, interval_seconds=60, num_days=100):
    """
    This function downloads the data at given frequency (interval seconds)
    for a given nunber of years for a given symbol from Google Finance
    """
    df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
    symbol = symbol.upper()
    # First try to download the data for index
    url_string = "http://finance.google.com/"
    url_string += "finance/getprices?q={0}".format(symbol)
    url_string += "&x=NYSE&p={0}d&i={1}".format(num_days, interval_seconds)
    url_string += '&f=d,o,h,l,c,v'

    # Exception handling done to take care of http errors
    try:
        csv = urlrequest.urlopen(url_string).readlines()
        # first 6 lines of the file contain static information
        for bar in range(7, len(csv)):
            l = csv[bar].decode('utf8')
            if l.count(',') != 5:
                continue  # the ohlcv data has 5 elements
            offset, close, high, low, open_, volume = l.replace(
                '\n', '').split(',')
            if offset[0] == 'a':  # offsets with prefix a contain dates
                day = float(offset[1:])
                offset = 0
            else:
                # offset without prefix a contain offset
                offset = float(offset)
            open_, high, low, close = [float(x)
                                       for x in [open_, high, low, close]]
            # unix timestamp converted to datetime
            dt = datetime.fromtimestamp(day + (interval_seconds * offset))
            # dataframe populated
            df.loc[dt, :] = [open_, high, low, close, volume]
    except Exception as e:
        print(e)
    # If data not found then try to download the data for NASDAQ
    if len(df) == 0:
        url_string = "http://finance.google.com/"
        url_string += "finance/getprices?q={0}".format(symbol)
        url_string += "&x=NASDAQ&p={0}d&i={1}".format(
            num_days, interval_seconds)
        url_string += '&f=d,o,h,l,c,v'
        # Exception handling done to take care of http errors
        try:
            csv = urlrequest.urlopen(url_string).readlines()
            # first 6 lines of the file contain static information
            for bar in range(7, len(csv)):
                l = csv[bar].decode('utf8')
                if l.count(',') != 5:
                    continue  # the ohlcv data has 5 elements
                offset, close, high, low, open_, volume = l.replace(
                    '\n', '').split(',')
                if offset[0] == 'a':  # offsets with prefix a contain dates
                    day = float(offset[1:])
                    offset = 0
                else:  # offset without prefix a contain offset
                    offset = float(offset)
                open_, high, low, close = [
                    float(x) for x in [
                        open_, high, low, close]]
                # unix timestamp converted to datetime
                dt = datetime.fromtimestamp(day + (interval_seconds * offset))
                # dataframe populated
                df.loc[dt, :] = [open_, high, low, close, volume]
        except Exception as e:
            print(e)
    # If data not found then try to download the data for NYSE
    if len(df) == 0:
        url_string = "http://finance.google.com/finance/getprices?q={0}".format(
            symbol)
        url_string += "&p={0}&i={1}d".format(num_days, interval_seconds)
        url_string += "&f=d,o,h,l,c,v"
        # Exception handling done to take care of http errors
        try:
            csv = urlrequest.urlopen(url_string).readlines()
            # first 6 lines of the file contain static information
            for bar in range(7, len(csv)):
                l = csv[bar].decode('utf8')
                if l.count(',') != 5:
                    continue  # the ohlcv data has 5 elements
                offset, close, high, low, open_, volume = l.replace(
                    '\n', '').split(',')
                if offset[0] == 'a':  # offsets with prefix a contain dates
                    day = float(offset[1:])
                    offset = 0
                else:  # offset without prefix a contain offset
                    offset = float(offset)
                open_, high, low, close = [
                    float(x) for x in [
                        open_, high, low, close]]
                # unix timestamp converted to datetime
                dt = datetime.fromtimestamp(day + (interval_seconds * offset))
                # dataframe populated
                df.loc[dt, :] = [open_, high, low, close, volume]
        except Exception as e:
            print(e)
    # datafrane returned
    return df

def download_fundamentals(symbol='AAPL'):
    '''
    This function downloads the fundamental data for the coponents of S&P 500
    from morningstar API and pushes it into separate databases called
    CASH_FLOW, BALANCE_SHEET and INCOME_STATEMENT
    '''
    kr = gm.FinancialsDownloader()
    kr_frames = kr.download('AAPL')
    cash_flow = kr_frames['cash_flow'].drop('parent_index', axis=1)
    cash_flow['symbol'] = symbol
    income_statement = kr_frames['income_statement'].drop(
        'parent_index', axis=1)
    income_statement['symbol'] = symbol
    balance_sheet = kr_frames['balance_sheet'].drop('parent_index', axis=1)
    balance_sheet['symbol'] = symbol
