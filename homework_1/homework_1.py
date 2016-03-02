import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sys import maxint, exit


class Helpers:
    @staticmethod
    def get_volatility(daily_returns):
        return np.std(daily_returns)

    @staticmethod
    def get_shrape_ratio(daily_return, volatility, trading_days):
        return np.sqrt(trading_days) * daily_return / volatility

    @staticmethod
    def get_cumulative_return(portfolio_values):
        return portfolio_values[portfolio_values.shape[0] - 1][0]

    @staticmethod
    def normalize_price_array(price_array_raw):
        return price_array_raw / price_array_raw[0, :]


class Optimizer:
    @staticmethod
    def simulate(start_date, end_date, symbols_list, allocation_list):
        timeofday_date = dt.timedelta(hours=16)
        timestamps_list = du.getNYSEdays(start_date, end_date, timeofday_date)

        # Let's use dynamic trading days count based on data
        trading_days = len(timestamps_list)

        keys_list = ['close']
        data_object = da.DataAccess('Yahoo', cachestalltime=0)
        data_list = data_object.get_data(timestamps_list,
                                         symbols_list,
                                         keys_list)
        data_dictionary = dict(zip(keys_list, data_list))

        price_array_raw = data_dictionary['close'].values.copy()
        price_array_normalized = Helpers.normalize_price_array(price_array_raw)
        allocation_vector = np.array(allocation_list).reshape(4, 1)
        portfolio_values = np.dot(price_array_normalized, allocation_vector)

        daily_returns = portfolio_values.copy()
        tsu.returnize0(daily_returns)

        # Compute volatility and mean (daily return) values of portfolio
        volatility = Helpers.get_volatility(daily_returns)
        daily_return = np.mean(daily_returns)
        # Compute Shrape ratio of portfolio
        shrape_ratio = Helpers.get_shrape_ratio(daily_return,
                                                volatility,
                                                trading_days)
        # Compute Cumulative Return of portfolio
        daily_cum_return = Helpers.get_cumulative_return(portfolio_values)

        return volatility, daily_return, shrape_ratio, daily_cum_return

    @staticmethod
    def optimize_allocation(start_date, end_date, symbols):
        if len(symbols) != 4:
            print """
            I'm sorry. I can only optimize allocation for 4 symbols.\n
            (exiting with status 1)
            """
            exit(1)

        max_shrape_ratio = -maxint - 1
        max_allocation = (0, 0, 0, 0)

        for i in np.arange(0, 11):
            for j in np.arange(0, 11 - i):
                for k in np.arange(0, 11 - i - j):
                    for l in np.arange(0, 11 - i - j - k):
                        if (i + j + k + l) == 10:
                            allocation = (i * .1, j * .1, k * .1, l * .1)
                            _, _, shrape_ratio, _ =  \
                                Optimizer.simulate(start_date, end_date,
                                                   symbols, allocation)
                            if shrape_ratio > max_shrape_ratio:
                                max_shrape_ratio = shrape_ratio
                                max_allocation = allocation
        return max_allocation

    @staticmethod
    def optimize_allocation_descent():
        pass

    @staticmethod
    def print_simulate(start_date, end_date, symbols, allocation):
        months = ['January', 'Febrary',
                  'March', 'April',
                  'May', 'June', 'July',
                  'August', 'September',
                  'October', 'November', 'December']

        volatility, daily_return, shrape_ratio, daily_cum_ret = \
            Optimizer.simulate(start_date, end_date, symbols, allocation)

        print 'Start date: %s %s, %s' % (months[start_date.month - 1],
                                         start_date.day, start_date.year)
        print 'End date: %s %s, %s' % (months[end_date.month - 1],
                                       end_date.day, end_date.year)
        print 'Symbols:', symbols
        print 'Optimal Allocations:', allocation
        print 'Shrape Ratio:', shrape_ratio
        print 'Volatility (stdev of daily returns):', volatility
        print 'Average Daily Return:', daily_return
        print 'Cumulative Return:', daily_cum_ret

    @staticmethod
    def print_optimized(start_date, end_date, symbols):
        allocation = Optimizer.optimize_allocation(start_date,
                                                   end_date,
                                                   symbols)
        Optimizer.print_simulate(start_date, end_date,
                                 symbols, allocation)


def main():
    start_date = dt.datetime(2010, 1, 1)
    end_date = dt.datetime(2010, 12, 31)
    symbols = ['C', 'GS', 'IBM', 'HNZ']

    Optimizer.print_optimized(start_date, end_date, symbols)


if __name__ == '__main__':
    main()
