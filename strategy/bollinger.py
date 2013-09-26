class Bollinger(object):
    """ Bollinger's band trading strategy, for Mean Reversion or Breakout

    Bollinger's band take 2 parameters the period N of the underlying moving
    average and the widht of the band K.

    To instantiate a 20 days, 2 standard dev:

    >>> bollinger = Bollinger(20, 2, reversion)
    """

    def __init__(self, n, k, strategy="reversion"):
        self.n = n
        self.k = k
        self.strategy = strategy

    def __call__(self, tick):
        if self.strategy == "breakout":
            if tick.close > tick.upper_bb(self.n, self.k):
                return 'buy'
            elif tick.close < tick.lower_bb(self.n, self.k):
                return 'sell'
        elif self.strategy == "reversion":
            if tick.close > tick.upper_bb(self.n, self.k):
                return 'sell'
            elif tick.close < tick.lower_bb(self.n, self.k):
                return 'buy'


