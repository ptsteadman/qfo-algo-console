class ChinaGap(object):
    """China Gap Strategy:
       Buys a stock if it opens X% lower than previous day's close
     """

    def __init__(self,x):
        self.x = x

    def __call__(self,tick):
        index = tick.index
        if ((tick.ma(3) - tick.series[index-3].ma(3)) / tick.series[index-3].ma(3))*100 < self.x:
            return 'buy'
        if (tick.ma(3)) > tick.upper_bb(30,2):
            return 'sell'
        else:
            return 'none'