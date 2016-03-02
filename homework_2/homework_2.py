import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep


def find_events(symbols, data):
    close = data['actual_close']

    print "Starting to find events..."
    # Events matrix
    e = copy.deepcopy(close)
    e = e * np.NAN

    # Timestamps array
    t = close.index

    for symbol in symbols:
        for i in np.arange(1, len(t)):
            symbol_price_today = close[symbol].ix[t[i]]
            symbol_price_yesterday = close[symbol].ix[t[i - 1]]
            if symbol_price_yesterday >= 10.00 > symbol_price_today:
                e[symbol].ix[t[i]] = 1

    return e


if __name__ == '__main__':
    start_date = dt.datetime(2008, 1, 1)
    end_date = dt.datetime(2009, 12, 31)
    timestamps = du.getNYSEdays(start_date,
                                end_date,
                                dt.timedelta(hours=16))

    data_object = da.DataAccess('Yahoo')
    symbols = data_object.get_symbols_from_list('sp5002008')
    symbols.append('SPY')

    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    raw_data = data_object.get_data(timestamps, symbols, keys)
    data = dict(zip(keys, raw_data))

    for key in keys:
        data[key] = data[key].fillna(method='ffill')
        data[key] = data[key].fillna(method='bfill')
        data[key] = data[key].fillna(1.0)

    events = find_events(symbols, data)
    print "Creating Study"
    ep.eventprofiler(events, data, i_lookback=20, i_lookforward=20,
                     s_filename='S&P5002008_10.pdf', b_market_neutral=True,
                     b_errorbars=True, s_market_sym='SPY')
