class Pairs(object):
    """ Trade based on changes in another stock/equity

        To instantiate a strategy that will SHORT target equity if 
        the parameter equity crosses the upper bollinger band, and BUY 
        the target equity if the parameter equity crosses the lower band:
     
    >>> vixPair = Pairs(VXX,20,1)

    (Parameter equity is VXX, and 20 day moving average / 1 standard deviation 
     for the bollinger band.)
    """

    def __init__(self, pair, n, k):
        self.n = n
        self.k = k
        self.pair = pair

    def __call__(self, tick):
        for t in self.pair:
            if t.date == tick.date:
                if t.close > t.upper_bb(self.n, self.k):
                    return 'buy'
                elif t.close < t.lower_bb(self.n, self.k):
                    return 'sell'


