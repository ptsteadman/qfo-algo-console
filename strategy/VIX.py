class Pairs(object):
    """ Trade based on changes in the another stock/equity
	
	

    Bollinger's band take 2 parameters the period N of the underlying moving
    average and the widht of the band K.

    To instantiate a 20 days, 2 standard dev:

    >>> vix = VIX(20, 2)
    """

    def __init__(self, pair, n, k):
        self.n = n
        self.k = k
        self.pair = pair

    def __call__(self, tick):
        for t in pair:
            if t.date() == tick.date():
                if tick.close > tick.upper_bb(self.n, self.k):
                    return 'sell'
            elif tick.close < tick.lower_bb(self.n, self.k):
                    return 'buy'

