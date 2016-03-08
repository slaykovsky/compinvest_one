# Computational Investing Part 1
# Year: 2015
# Author: Alexey Slaykovsky <alexey@slaykovsky.com>


import pandas as pd
import numpy as np


def get(data, lookback_period):
    close_data = data["close"]

    symbols = close_data.columns.values

    temp = np.zeros((len(close_data), 0))

    moving_average = pd.DataFrame(temp, index=close_data.index)
    moving_volatility = pd.DataFrame(temp, index=close_data.index)
    bollinger_close_data = pd.DataFrame(temp, index=close_data.index)

    for symbol in symbols:
        moving_average[symbol] = pd.Series(pd.rolling_mean(close_data[symbol], lookback_period),
                                           index=moving_average.index)
        moving_volatility[symbol] = pd.Series(pd.rolling_std(close_data[symbol], lookback_period),
                                              index=moving_volatility.index)
        bollinger_close_data[symbol] = (close_data[symbol] - moving_average[symbol]) / moving_volatility[symbol]

    return bollinger_close_data
