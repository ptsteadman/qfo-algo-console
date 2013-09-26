class RSI(object):
    """ Trade based on Relative Strength Index oscillator

    """

    def __init__(self, n):
        self.n = n

    def __call__(self, tick):
                if tick.rsi(self.n) > 70:
                    return 'sell'
                elif tick.rsi(self.n) < 30:
                    return 'buy'