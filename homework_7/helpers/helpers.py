from __future__ import division

import datetime as dt

import pandas as pd
import pandas.io.parsers as pd_parsers
import numpy as np

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da


TRADING_DAYS_AMOUNT = 252


def get_data(file_path):
    data = pd_parsers.read_csv(file_path, header=None)
    # data.drop(6, inplace=True, axis=1)
    return data


def get_data_dict(keys, symbols, timestamps):
    data_object = da.DataAccess('Yahoo')
    raw_data = data_object.get_data(timestamps,
                                    symbols,
                                    keys)
    return dict(zip(keys, raw_data))


def make_trade_data(symbols, timestamps):
    """
    As symbols here is the reference to the global list of symbols
    appending Cash to it is applied for referenced global list
    """
    symbols.append('Cash')
    return pd.DataFrame(index=list(timestamps),
                        columns=list(symbols))


def make_cash_data(timestamps, symbols, trade_data, close_data):
    cash_data = pd.DataFrame(index=list(timestamps),
                             columns=['Cash'])
    cash_data.fillna(0, inplace=True)

    for day in timestamps:
        cash = 0
        for symbol in symbols:
            if symbol == "Cash":
                cash += trade_data[symbol][day]
            else:
                cash += close_data[symbol][day] * trade_data[symbol][day]
        cash_data['Cash'][day] = cash

    return cash_data


def get_symbols_from_data(data):
    return list(set(data[3].values))


def get_start_date(data):
    return dt.datetime(data.get_value(0, 0),
                       data.get_value(0, 1),
                       data.get_value(0, 2), 16)


def get_end_date(data):
    last = len(data) - 1
    return dt.datetime(data.get_value(last, 0),
                       data.get_value(last, 1),
                       data.get_value(last, 2), 16)


def get_timestamps(start_date, end_date):
    return du.getNYSEdays(start_date,
                          end_date,
                          dt.timedelta(hours=16))


def normalize_data(data):
    return data / data[0]


def get_daily_return(daily_values):
    return np.mean(daily_values)


def get_volatility(daily_values):
    return np.std(daily_values)


def get_shrape_ratio(daily_return, volatility):
    return np.sqrt(TRADING_DAYS_AMOUNT) * daily_return / volatility


def get_cummulative_return(values):
    return values[-1] / values[0]
