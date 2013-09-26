class BasicGap(object):
    """Basic Gap Strategy:
       Buys a stock if it opens X% lower than previous day's close
       Sells at the close of the day. """

    def __init__(self,x):
        self.x = x

    def __call__(self,tick):
        index = tick.index
        self.gap = ((tick.open - tick.series[index-1].close)/ tick.series[index-1].close)*100
        if self.gap < self.x:
            return 'buyopen'
        else:
            return 'none'
