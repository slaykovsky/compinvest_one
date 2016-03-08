# Computational Investing Part 1
# Year: 2015
# Author: Alexey Slaykovsky <alexey@slaykovsky.com>


"""
Part 1: Implement Bollinger bands as an indicator using 20 day look back.
    Create code that generates a chart showing the rolling mean, the stock price, and upper and lower bands.
    The upper band should represent the mean plus one standard deviation and here the lower band is the mean
    minus one standard deviation. Traditionally the upper and lower Bollinger bands are 2 standard deviations
    but for this assignment we would use a tighter band of 1 or a single standard deviation.
Part 2: Have your code output the indicator value in a range of -1 to 1. Yes, those values can be exceeded,
    but the intent is that +1 represents the situation where the price is at +1 standard deviations above the mean.
    To convert the present value of Bollinger bands into -1 to 1:
Bollinger_val = (price - rolling_mean) / (rolling_std)
Part 3: Implement an indicator of your choice and have it report in a range of -1 to 1.
"""
import sys
import pandas as pd
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import matplotlib.pyplot as plt


def main():
    try:
        start_date_arg = sys.argv[1].split(",")
        end_date_arg = sys.argv[2].split(",")
        symbols = sys.argv[3].split(",")
        lookback_period = int(sys.argv[4])
    except Exception as e:
        print str(e)
        sys.exit(1)

    start_date_ints = map(int, start_date_arg)
    end_date_ints = map(int, end_date_arg)

    start_date = dt.datetime(start_date_ints[0], start_date_ints[1], start_date_ints[2])
    end_date = dt.datetime(end_date_ints[0], end_date_ints[1], end_date_ints[2])

    timestamps = du.getNYSEdays(start_date, end_date, dt.timedelta(hours=16))

    data_object = da.DataAccess('Yahoo')

    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    raw_data = data_object.get_data(timestamps, symbols, keys)
    data = dict(zip(keys, raw_data))

    for key in keys:
        data[key] = data[key].fillna(method='ffill')
        data[key] = data[key].fillna(method='bfill')
        data[key] = data[key].fillna(1.0)

    close_data = data["close"]
    mean_close_data = pd.rolling_mean(close_data, lookback_period)
    volatility_close_data = pd.rolling_std(close_data, lookback_period)

    bollinger_close_data = (close_data - mean_close_data)/volatility_close_data

    upper_moving_average = mean_close_data + volatility_close_data
    lower_moving_average = mean_close_data - volatility_close_data

    plt.plot(timestamps, upper_moving_average)
    plt.plot(timestamps, close_data)
    plt.plot(timestamps, lower_moving_average)
    plt.show()

    print bollinger_close_data.to_string()


if __name__ == "__main__":
    main()