import pandas.io.parsers as pd_parsers
import numpy as np


TRADING_DAYS_AMOUNT = 252


def get_cash_data(values_file_path):
    cash_data = pd_parsers.read_csv(values_file_path,
                                    header=None)
    cash_data.drop(4, inplace=True, axis=1)
    return cash_data


def normalize_data(data):
    return np.float64(data) / data[0]


def get_daily_return(daily_values):
    return np.mean(daily_values)


def get_volatility(daily_values):
    return np.std(daily_values)


def get_shrape_ratio(daily_return, volatility):
    return np.sqrt(TRADING_DAYS_AMOUNT) * daily_return / volatility


def get_cummulative_return(values):
    return values[-1] / values[0]
