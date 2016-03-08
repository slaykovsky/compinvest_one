# Computational Investing Part 1
# Year: 2015
# Author: Alexey Slaykovsky <alexey@slaykovsky.com>


import sys

import pandas as pd
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import boillinger as bo
import events as ev


def main():
    try:
        start_date_arg = sys.argv[1].split(",")
        end_date_arg = sys.argv[2].split(",")
        lookback_period = int(sys.argv[3])
        eq_today = float(sys.argv[4])
        eq_yesterday = float(sys.argv[5])
        spy_today = float(sys.argv[6])
    except Exception as e:
        print str(e)
        sys.exit(1)

    start_date_ints = map(int, start_date_arg)
    end_date_ints = map(int, end_date_arg)

    start_date = dt.datetime(start_date_ints[0], start_date_ints[1], start_date_ints[2])
    end_date = dt.datetime(end_date_ints[0], end_date_ints[1], end_date_ints[2])

    timestamps = du.getNYSEdays(start_date, end_date, dt.timedelta(hours=16))

    data_object = da.DataAccess('Yahoo')

    symbols = data_object.get_symbols_from_list('sp5002012')
    symbols.append('SPY')

    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    raw_data = data_object.get_data(timestamps, symbols, keys)
    data = dict(zip(keys, raw_data))

    for key in keys:
        data[key] = data[key].fillna(method='ffill')
        data[key] = data[key].fillna(method='bfill')
        data[key] = data[key].fillna(1.0)

    bollinger_close_data = bo.get(data, lookback_period)

    events = ev.find(bollinger_close_data, eq_today, eq_yesterday, spy_today)

    ep.eventprofiler(events, data, i_lookback=lookback_period, i_lookforward=lookback_period,
                     s_filename='boillinger.pdf', b_market_neutral=True,
                     b_errorbars=True, s_market_sym='SPY')


if __name__ == "__main__":
    main()