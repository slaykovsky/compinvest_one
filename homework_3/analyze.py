import sys

import pandas as pd

import QSTK.qstkutil.tsutil as tsu

import marketsim
import helpers.helpers as helpers


def main():
    values_file_path = sys.argv[1]
    benchmarks = [sys.argv[2]]

    cash_data = helpers.get_cash_data(values_file_path)

    start_date = marketsim.get_start_date(cash_data)
    end_date = marketsim.get_end_date(cash_data)

    keys = ['close']

    timestamps = marketsim.get_timestamps(start_date, end_date)
    data = marketsim.get_data(keys, benchmarks, timestamps)

    benchmark_values = data['close'].values.copy()
    benchmark_values = helpers.normalize_data(benchmark_values)

    fund_values = cash_data[3].values.copy()
    fund_values = helpers.normalize_data(fund_values)

    fund_daily_values = fund_values.copy()
    tsu.returnize0(fund_daily_values)

    benchmark_daily_values = benchmark_values.copy()
    tsu.returnize0(benchmark_daily_values)

    fund_daily_return = helpers.get_daily_return(fund_daily_values)
    fund_volatility = helpers.get_volatility(fund_daily_values)
    fund_shrape_ratio = helpers.get_shrape_ratio(fund_daily_return,
                                                 fund_volatility)
    fund_cummulative_return = helpers.get_cummulative_return(fund_values)

    benchmark_daily_return = helpers.get_daily_return(benchmark_daily_values)
    benchmark_volatility = helpers.get_volatility(benchmark_daily_values)
    benchmark_shrape_ratio = helpers.get_shrape_ratio(benchmark_daily_return,
                                                      benchmark_volatility)
    benchmark_cummulative_return = \
        helpers.get_cummulative_return(benchmark_values)

    print "Details of the Performance of the portfolio :\n"
    print "Data Range : %s to %s\n" % (start_date, end_date)
    print "Shrape Ratio of Fund : %s" % (fund_shrape_ratio)
    for benchmark in benchmarks:
        print "Shrape Ratio of %s : %s" % (benchmark, benchmark_shrape_ratio)
    print
    print "Total Return of Fund : %s" % (fund_cummulative_return)
    for benchmark in benchmarks:
        print "Total Return of %s : %s" % (benchmark,
                                           benchmark_cummulative_return)
    print
    print "Standard Deviation of Fund : %s" % (fund_volatility)
    for benchmark in benchmarks:
        print "Standard Deviation of %s : %s" % (benchmark,
                                                 benchmark_volatility)
    print
    print "Average Daily Return of Fund : %s" % (fund_daily_return)
    for benchmark in benchmarks:
        print "Average Daily Return of %s : %s" % (benchmark,
                                                   benchmark_daily_return)


if __name__ == "__main__":
    main()
