# Computational Investing Part 1
# Year: 2015
# Author: Alexey Slaykovsky <alexey@slaykovsky.com>

import sys
import datetime as dt

import numpy as np


def write_cash_data(cash_data, values_file_path):
    with open(values_file_path, "w") as values_file:
        for row in cash_data.iterrows():
            values_file.writelines(",".join([str(row[0].strftime("%Y,%m,%d")),
                                             str(row[1]["Cash"]), "\n"]))


def main():
    starting_cash = np.float64(sys.argv[1])
    orders_file_path = sys.argv[2]
    values_file_path = sys.argv[3]

    orders_data = get_orders_data(orders_file_path)

    symbols = get_symbols_from_orders_data(orders_data)
    start_date = get_start_date(orders_data)
    end_date = get_end_date(orders_data)

    timestamps = get_timestamps(start_date, end_date)

    keys = ['close']

    data = get_data(keys, symbols, timestamps)
    close_data = data['close']
    trade_data = make_trade_data(symbols, timestamps)

    current_cash = starting_cash

    trade_data['Cash'][timestamps[0]] = starting_cash

    current_stocks = dict()
    for symbol in symbols:
        current_stocks[symbol] = 0
        trade_data[symbol][timestamps[0]] = 0

    for row in orders_data.iterrows():
        row_data = row[1]
        current_date = dt.datetime(row_data[0],
                                   row_data[1],
                                   row_data[2], 16)
        symbol = row_data[3]
        stock_value = data['close'][symbol][current_date]
        stock_amount = row_data[5]

        action = row_data[4]

        if action == "Buy":
            current_cash -= stock_value * stock_amount
            current_stocks[symbol] += stock_amount
            trade_data['Cash'][current_date] = current_cash
            trade_data[symbol][current_date] = current_stocks[symbol]
        elif action == "Sell":
            current_cash += stock_value * stock_amount
            current_stocks[symbol] -= stock_amount
            trade_data['Cash'][current_date] = current_cash
            trade_data[symbol][current_date] = current_stocks[symbol]

    trade_data.fillna(method="pad",
                      inplace=True)

    cash_data = make_cash_data(timestamps,
                               symbols,
                               trade_data,
                               close_data)

    write_cash_data(cash_data, values_file_path)


if __name__ == '__main__':
    main()
