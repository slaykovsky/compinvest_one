# Computational Investing Part 1
# Year: 2015
# Author: Alexey Slaykovsky <alexey@slaykovsky.com>

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import pandas as pd
import numpy as np

import sys
import csv


def read_orders(filename):
    # opening the filename
    fr = open(filename)

    # for row count in
    index = 0

    # Lists used for making the dataframe.
    dtList = []
    symbolList = []
    orderTypeList = []
    volumeList = []

    # For each line
    # A Sample Line - 2011,1,14,AAPL,Buy,1500
    for orderString in fr.readlines():
        # Stripping off the return line character
        orderString = orderString.strip()

        # Splitting the line and getting a List back
        listFromLine = orderString.split(',')

        # Adding the dates into dtList. 16,00,00 for 1600 hrs
        dtList.append(dt.datetime(int(listFromLine[0]), int(listFromLine[1]), int(listFromLine[2]), 16, 00, 00))

        # Adding the symbols into symbolList
        symbolList.append(listFromLine[3])

        # Adding the orders into orderTypeList
        orderTypeList.append(listFromLine[4])

        # Adding the number of shares into volumeList
        volumeList.append(listFromLine[5])

    # Creating a Dictionary for converting it into DataFrame later
    data = {'datetime': dtList, 'symbol': symbolList, 'ordertype': orderTypeList, 'volume': volumeList}

    # Converting the Dictinary into a nice looking Pandas Dataframe
    ordersDataFrame = pd.DataFrame(data)

    # Sorting by datetime column #Makes Sense :)
    sortedOrdersDataFrame = ordersDataFrame.sort_index(by=['datetime'])
    sortedOrdersDataFrame = sortedOrdersDataFrame.reset_index(drop=True)

    # Making the datetime columns as the index and removing it from the table
    # sortedOrdersDataFrame.index = sortedOrdersDataFrame.datetime
    # del sortedOrdersDataFrame['datetime']

    # Getting the Symbols from the Orders. This list will be required for fetching the prices
    symbolList = list(set(sortedOrdersDataFrame['symbol']))

    # Returning it.
    return sortedOrdersDataFrame, symbolList


def fetchNYSEData(dt_start, dt_end, ls_symbols):
    # The Time of Closing is 1600 hrs
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    timestampsForNYSEDays = d_data['close'].index

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values

    # returning the closed prices for all the days
    return na_price, ldt_timestamps


def marketsim(initial_cash, orders_data_frame, symbols):
    # reading the boundary dates
    dt_start = orders_data_frame.datetime[0]
    dt_end = orders_data_frame.datetime[len(orders_data_frame) - 1]

    # All the adjustedClosingPrices fetched from NYSE within the range and for given symbols
    closingPrices, ldt_timestamps = fetchNYSEData(dt_start, dt_end, symbols)

    trading_days_amount = len(ldt_timestamps)

    # For Holdings of the share
    temp = np.zeros((1, len(symbols)))
    holdings = pd.DataFrame(temp, columns=symbols, index=['holdings'])

    # Cash for the days
    temp = np.zeros((trading_days_amount, 1))
    cash = pd.DataFrame(temp, columns=['cashinhand'])

    # Value for the days
    temp = np.zeros((trading_days_amount, 1))
    value_frame = pd.DataFrame(temp, columns=['value_of_portfolio'])

    # Setting the first value to be the initial cash amount.
    cash.cashinhand.ix[0] = initial_cash

    index = 0

    for trading_day_index in range(trading_days_amount):
        if trading_day_index != 0:
            cash.cashinhand.ix[trading_day_index] = cash.cashinhand.ix[trading_day_index - 1]
        else:
            cash.cashinhand.ix[trading_day_index] = initial_cash

        for tradingOrder in orders_data_frame.datetime:
            if tradingOrder == ldt_timestamps[trading_day_index]:
                if orders_data_frame.ordertype.ix[index] == 'Buy':
                    buy_symbol = orders_data_frame.symbol.ix[index]
                    to_buy = symbols.index(buy_symbol)
                    shares_amount = orders_data_frame.volume.ix[index]
                    price_for_the_day = closingPrices[trading_day_index, to_buy]
                    cash.cashinhand.ix[trading_day_index] -= float(price_for_the_day) * int(shares_amount)
                    holdings[buy_symbol].ix[0] += int(shares_amount)
                elif orders_data_frame.ordertype.ix[index] == 'Sell':
                    sell_symbol = orders_data_frame.symbol.ix[index]
                    to_sell = symbols.index(sell_symbol)
                    shares_amount = orders_data_frame.volume.ix[index]
                    price_for_the_day = closingPrices[trading_day_index, to_sell]
                    cash.cashinhand.ix[trading_day_index] += float(price_for_the_day) * int(shares_amount)
                    holdings[sell_symbol].ix[0] -= int(shares_amount)
                else:
                    print "error"
                index += 1

        value_from_portfolio = 0

        for symbol in symbols:
            price_for_the_day = closingPrices[trading_day_index, symbols.index(symbol)]
            value_from_portfolio += holdings[symbol].ix[0] * price_for_the_day

        value_frame.value_of_portfolio.ix[trading_day_index] = value_from_portfolio + cash.cashinhand.ix[trading_day_index]

    value_frame.index = ldt_timestamps
    return holdings, value_frame, cash


def writeValuesIntoCSV(valuesFilename, valueFrame):
    file = open(valuesFilename, 'w')
    writer = csv.writer(file)

    for index in range(len(valueFrame)):
        writer.writerow([valueFrame.index[index].year, valueFrame.index[index].month, valueFrame.index[index].day,
                         int(round(valueFrame.value_of_portfolio.ix[index], 0))])

    file.close()


def analyze(values):
    symbols = ['$SPX']

    dt_start = values.index[0]
    dt_end = values.index[len(values) - 1]

    # All the adjustedClosingPrices fetched from NYSE within the range and for given symbols
    spx_closing_prices, ldt_timestamps = fetchNYSEData(dt_start, dt_end, symbols)

    trading_days_amount = len(ldt_timestamps)
    daily_returns = np.zeros((trading_days_amount, 2))
    cummulative_returns = np.zeros((trading_days_amount, 2))

    # The first day prices of the equities
    first_day_prices = [spx_closing_prices[0, 0], values.value_of_portfolio.ix[0]]

    for i in range(trading_days_amount):
        if i != 0:
            daily_returns[i, 0] = ((spx_closing_prices[i, 0] / spx_closing_prices[i - 1, 0]) - 1)
            daily_returns[i, 1] = ((values.value_of_portfolio.ix[i] / values.value_of_portfolio.ix[i - 1]) - 1)

    for i in range(trading_days_amount):
        if i != 0:
            cummulative_returns[i, 0] = (spx_closing_prices[i, 0] / first_day_prices[0])
            cummulative_returns[i, 1] = (values.value_of_portfolio.ix[i] / first_day_prices[1])

    average_spx_daily_returns = np.average(daily_returns[:, 0])
    average_portfolio_daily_returns = np.average(daily_returns[:, 1])

    volatility_spx = np.std(daily_returns[:, 0])
    volatility_portfolio = np.std(daily_returns[:, 1])

    total_spx_return = cummulative_returns[-1, 0]
    total_portfolio_return = cummulative_returns[-1, 1]

    k = 252
    sharpe_ratio_spx = (k ** (1 / 2.0)) * (average_spx_daily_returns / volatility_spx)
    sharpe_ratio_portfolio = (k ** (1 / 2.0)) * (average_portfolio_daily_returns / volatility_portfolio)

    print "The final value of the portfolio using the sample file is -- {0},{1},{2},{3}".format(dt_end.year,
                                                                                                dt_end.month,
                                                                                                dt_end.day,
                                                                                                values.value_of_portfolio.ix[-1])

    print "Details of the Performance of the portfolio"
    print
    print "Data Range :", ldt_timestamps[0], " to ", ldt_timestamps[-1]
    print
    print "Sharpe Ratio of Fund :", sharpe_ratio_portfolio
    print "Sharpe Ratio of $SPX :", sharpe_ratio_spx
    print
    print "Total Return of Fund :", total_portfolio_return
    print "Total Return of $SPX :", total_spx_return
    print
    print "Standard Deviation of Fund :", volatility_portfolio
    print "Standard Deviation of $SPX :", volatility_spx
    print
    print "Average Daily Return of Fund :", average_portfolio_daily_returns
    print "Average Daily Return of $SPX :", average_spx_daily_returns


def main():
    print 'Argument List:', str(sys.argv)

    initial_cash = float(sys.argv[1])
    orders_path = sys.argv[2]
    values_path = sys.argv[3]

    # Reading the data from the file, and getting a NumPy matrix
    orders_data, symbols = read_orders(orders_path)
    holdings, values, cash = marketsim(initial_cash, orders_data, symbols)

    writeValuesIntoCSV(values_path, values)

    analyze(values)


if __name__ == '__main__':
    main()
