from collections import namedtuple
import datetime

import numpy


numpy.seterr(invalid='ignore')

class Tick(namedtuple('Tick',
                      ['series', 'index', 'date', 'open', 'high', 'low',
                       'close', 'volume', 'adj'])):
    """ Tick i.e. stock price etc. on a given day

    Contains a reference to the time series it belongs to (Stock.data) and its
    index in the list in order to compute metrics.

    >>> Tick([], 0, datetime.date(2012, 5, 25), 1.0, 1.0, 1.0,
    ...              1.0, 1, 1.0)
    Tick(series=[...], index=0, date=2012-05-25 open=1.0, high=1.0, low=1.0, close=1.0, volume=1, adj=1.0)
    """

    __slots__ = ()

    def __repr__(self):
        return 'Tick(series=[...], index={0.index}, date={0.date} \
open={0.open}, high={0.high}, low={0.low}, close={0.close}, \
volume={0.volume}, adj={0.adj})'.format(self)

    def std(self, n):
        index = self.index + 1
        return numpy.std([tick.close for tick in self.series[index-n:index]])

    def ma(self, n):
        index = self.index + 1
        return numpy.mean([tick.close for tick in self.series[index-n:index]])

    def first_avg_gain(self,n):
        gain = 0
        counter=0
        for tick in self.series[0:n]:
            if tick.series[counter+1].close >= tick.series[counter].close:
                gain = gain + (tick.series[counter+1].close - tick.series[counter].close)
            counter = counter + 1
        return (gain/n)

    def first_avg_loss(self,n):
        loss = 0
        counter=0
        for tick in self.series[0:n]:
            if tick.series[counter+1].close <= tick.series[counter].close:
                loss = loss + (tick.series[counter].close - tick.series[counter+1].close)
            counter = counter + 1
        return (loss/n)

    def avg_gain(self,n):
        index = self.index
        gain = self.first_avg_gain(n)
        counter = n
        daysgain = 0
        while counter <= index:
            if self.series[counter].close >= self.series[counter-1].close:
                daysgain = self.series[counter].close - self.series[counter-1].close
            gain = ((gain * (n-1)) + daysgain) / float(n)
            counter = counter + 1
        return gain

    def avg_loss(self,n):
        index = self.index
        loss = self.first_avg_loss(n)
        counter = n
        daysloss = 0
        while counter <= index:
            if self.series[counter-1].close >= self.series[counter].close:
                daysloss = self.series[counter-1].close - self.series[counter].close
            loss = ((loss * (n-1)) + daysloss) / float(n)
            counter = counter + 1
        return loss

    def rsi(self,n):
        rs = self.avg_gain(n) / self.avg_loss(n)
        rsi = 100.0 - (100.0 / (1 + rs))
        return rsi

    def upper_bb(self, n, k):
        return self.ma(n) + k * self.std(n)

    def lower_bb(self, n, k):
        return self.ma(n) - k * self.std(n)


