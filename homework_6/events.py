import copy
from numpy import arange, NAN


def find(data, eq_today, eq_yesterday, spy_today):
    symbols = data.columns.values
    market = data['SPY']

    print "Starting to find events..."
    # Events matrix
    e = copy.deepcopy(data)
    e = e * NAN

    # Timestamps array
    t = data.index

    for symbol in symbols:
        for i in arange(1, len(t)):
            value_today = data[symbol].ix[t[i]]
            value_yesterday = data[symbol].ix[t[i - 1]]
            market_today = market[t[i]]

            if value_today <= eq_today and value_yesterday >= eq_yesterday and market_today >= spy_today:
                e[symbol].ix[t[i]] = 1
    return e
