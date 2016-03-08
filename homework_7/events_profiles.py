# Computational Investing Part 1
# Year: 2015
# Author: Alexey Slaykovsky <alexey@slaykovsky.com>

import sys
import csv

import numpy as np
import copy
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import boillinger as bo
import helpers.helpers as hp

def get_events(symbols, data_dict, event_amount, orders_file_path):
    with open(orders_file_path, "w") as orders_file:
        writer = csv.writer(orders_file)

        actual_close = data_dict['actual_close']

        boillinger = bo.get(data_dict, 20)

        market = boillinger['SPY']

        print "Starting to find events..."

        events = copy.deepcopy(boillinger)
        events = events * np.NAN

        timestamps = boillinger.index

        for symbol in symbols:
            for i in range(1, len(timestamps)):
                price_today = boillinger[symbol].ix[timestamps[i]]
                price_yesterday = boillinger[symbol].ix[timestamps[i - 1]]
                market_today = market[timestamps[i]]

                if price_today <= -2 <= price_yesterday and market_today >= 1.4:
                    buy_date = timestamps[i]
                    try:
                        sell_date = timestamps[i + 5]
                    except:
                        sell_date = timestamps[-1]

                    writer.writerow([buy_date.year,
                                     buy_date.month,
                                     buy_date.day,
                                     symbol,
                                     "Buy", "100"])
                    writer.writerow([sell_date.year,
                                     sell_date.month,
                                     sell_date.day,
                                     symbol,
                                     "Sell", "100"])

                    events[symbol].ix[timestamps[i]] = 1

        return events


def main():
    try:
        start_date = sys.argv[1].split(',')
        end_date = sys.argv[2].split(',')
        spx = sys.argv[3]
        orders_file = sys.argv[4]
        event_amount = np.float32(sys.argv[5])
        chart_path = sys.argv[6]
    except Exception as e:
        print str(e)
        print "You need to specify three arguments here:"
        print "\tstart date (e.g. 2008,01,01)"
        print "\tend date (e.g. 2009,12,31)"
        print "\tspx (e.g. sp5002012)"
        print "\torders file path (e.g. orders.csv)"
        print "\tevent amount as number (e.g. 10)"
        print "\tchart file path (e.g. chart.pdf)"
        print "Usage:"
        print sys.argv[0] + " [start_date] [end_date] [spx] [order_file] [event_amount] [chart_path]"
        sys.exit(1)

    start_date = dt.datetime(int(start_date[0]),
                             int(start_date[1]),
                             int(start_date[2]))
    end_date = dt.datetime(int(end_date[0]),
                           int(end_date[1]),
                           int(end_date[2]))

    timestamps = hp.get_timestamps(start_date, end_date)

    data_object = da.DataAccess('Yahoo')
    symbols = data_object.get_symbols_from_list(spx)

    symbols.append('SPY')

    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    raw_data = data_object.get_data(timestamps, symbols, keys)
    data = dict(zip(keys, raw_data))

    for key in keys:
        data[key] = data[key].fillna(method='ffill')
        data[key] = data[key].fillna(method='bfill')
        data[key] = data[key].fillna(1.0)

    events = get_events(symbols, data, event_amount, orders_file)

    ep.eventprofiler(events, data, i_lookback=20, i_lookforward=20,
                     s_filename=chart_path, b_market_neutral=True,
                     b_errorbars=True, s_market_sym='SPY')


if __name__ == '__main__':
    main()
