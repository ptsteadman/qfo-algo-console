import datetime
import cPickle as pickle
import re

from ext.ystockquote import get_historical_prices
from matplotlib.pyplot import plot, savefig, clf

from tick import Tick
from StockKeyStatLib import KeyStats


class Stock(object):
    """ List like stock data for a given symbol

    Loads from Yahoo when instantiated unless cache is available.

    >>> goog = Stock('GOOG')
    >>> goog
    Stock(symbol=GOOG, data=[1958])
    >>> isinstance(goog[0], Tick)
    True
    """

    def __init__(self, symbol=None, option=None,yahoo=get_historical_prices, earnings = None):
        self.yahoo = yahoo
        self.symbol = symbol
        self.option = option
        self.earnings = earnings
        self.data = []
        if symbol is not None:
            if self.option == 'cache':
                self.load_cached(symbol)
            else:
                self.load(symbol)

    def __repr__(self):
        return "Stock(symbol={0}, data=[{1}])".format(self.symbol, len(self.data))

    def print_earnings_summary(self, days = 10):
        self.days = days
        print "Earnings Summary For: " + str(self.symbol) + "+"
        i = None
        for t in self:    # Find the index of the earnings date
            if t.date == self.earnings:
                i = t.index
        if i is not None: 
            print '10 Days Prior Earnings Performance:       {!s:7}%'.format(str(round(((self[i-10].close - self[i].close) / self[i-10].close)*100,2)))
            print '10 Days After Earnings Performance:       {!s:7}%'.format(str(round(((self[i].close - self[i+10].close) / self[i].close)*100,2)))
            print 'Volume on Day of Earnings:                {!s:7}'.format(str(self[i].volume))
            print 'Performance on Day of Earnings:           {!s:7}%'.format(str(round(((self[i].close-self[i-1].close)/self[i-1].close)*100,3)))
            print 'Close Position Ratio on Day of Earnings:  {!s:7}'.format(str(round((self[i].close-self[i].low)/(self[i].high - self[i].low),2)))
            before = self[i-10:i]
            total = 0
            for t in before:
                total = total + t.volume
            print 'Average Volume 10 Days Prior to Earnings: {!s:7}'.format(str( total / len(before)))
            after = self[i:i+10]
            total = 0
            for t in after:
                total = total + t.volume
            print 'Average Volume 10 Days After Earnings:    {!s:7}'.format(str( total / len(after)))
        else:
            print "Date not valid trading date: Stock"
        spy = Stock("SPY")
        j = None
        for t in spy:  # Find the index in SPY of the earnings date
            if t.date == self.earnings:
                j = t.index
        if j is not None: 
            print '10 Days Prior Earnings SPY Performance:   {!s:7}%'.format(str(round(((spy[j-10].close - spy[j].close) / spy[j-10].close)*100,2)))
            print '10 Days After Earnings SPY Performance:   {!s:7}%'.format(str(round(((spy[j].close - spy[j+10].close) / spy[j].close)*100,2)))
            print 'Performance on Day of Earnings:           {!s:7}%'.format(str(round(((self[i].close-self[i-1].close)/self[i-1].close)*100,3)))
        else:
            print "Date not valid trading date: Market."
        print "\n"
         
    def return_summary_dict(self):
        DAYS = 10    #contstant variable for date range around earnings
        summary = dict()
        spy = Stock("SPY")
        i = None
        for t in self:
            if t.date == self.earnings:
                i = t.index
        j = None
        for t in spy:
            if t.date == self.earnings:
                j = t.index
        if i is not None and j is not None:
            summary['ticker'] = self.symbol
            summary['DaysPriorPerformance'] =  ((self[i - 1].adj - self[i-DAYS - 1].adj) / self[i - DAYS - 1].adj)*100
            summary['DaysPriorSpyPerformance'] = ((spy[j-1].adj - spy[j-DAYS-1].adj) / spy[j - DAYS - 1].adj)*100
            summary['DaysPriorAvgVolume'] = self.get_avg_volume("before",DAYS, i)
            summary['DayOfPerformance'] = ((self[i].adj-self[i-1].adj)/self[i-1].adj)*100
            summary['DayOfVolume'] = self[i].volume
            summary['DayOfMarketPerformance'] = ((spy[j].adj-spy[j-1].adj)/spy[j-1].adj)*100
            summary['ClosePositionRatio'] = (self[i].close-self[i].low)/(self[i].high - self[i].low)
            summary['DaysAfterPerformance'] =  ((self[i+DAYS].adj - self[i].adj) / self[i].adj)*100
            summary['DaysAfterSpyPerformance'] = ((spy[j+DAYS].adj - spy[j].adj) / spy[j].adj)*100
            summary['DaysAfterAvgVolume'] = self.get_avg_volume("after",DAYS, i)
            summary['KeyStatsDict'] = KeyStats(self.symbol).KeyStatsDict
            return summary 
        else:
            return summary
        
    def get_avg_volume(self,beforeOrAfter, days, i):
        if beforeOrAfter == "before":
            period = self[i-days:i-1]
        if beforeOrAfter == "after":
            period = self[i + 1: i + days]
        total = 0
        for t in period:
            total = total + t.volume
        return total / len(period)

    def load_cached(self, symbol):
        """ Loads the stock quote for symbol from Yahoo or cache """
        raw = Stock.get_old_from_cache(symbol,'2012-12-25')
        # Tick aware of the time series it belongs to
        self.data.extend(
            [ Tick(self.data, index, *Stock.cast(tick))
              for index, tick
              in enumerate(reversed(raw[1:])) ])

    def load(self, symbol):
        """ Loads the stock quote for symbol from Yahoo or cache """
        raw = Stock.get_from_cache(symbol)
        if raw is None:
            today = datetime.date.today().strftime('%Y%m%d')
            raw = self.yahoo(symbol, '20010103', today)
            Stock.save_to_cache(symbol, raw)
        # Tick aware of the time series it belongs to
        self.data.extend(
            [ Tick(self.data, index, *Stock.cast(tick))
              for index, tick
              in enumerate(reversed(raw[1:])) ])

    @staticmethod
    def get_old_from_cache(symbol,date):
        """ Get the date for symbol from cache return list or none """
        try:
            with open('cache/{0}_{1}'.format(symbol,date)) as f:
                return pickle.load(f)
        except (IOError, EOFError):
            return None

    @staticmethod
    def get_from_cache(symbol):
        """ Get the date for symbol from cache return list or none """
        try:
            with open('cache/{0}_{1}'.format(symbol, datetime.date.today())) as f:
                return pickle.load(f)
        except (IOError, EOFError):
            return None

    @staticmethod
    def save_to_cache(symbol, raw):
        """ Save the data coming from Yahoo into cache """
        f = open('cache/{0}_{1}'.format(symbol, datetime.date.today()), 'w')
        pickle.dump(raw, f)

    @staticmethod
    def cast(raw_tick):
        """ Cast the data from a Yahoo raw tick into relevant types

        >>> Stock.cast(('2012-05-25', '1.0'))
        [datetime.date(2012, 5, 25), 1.0]
        """
        result = [ datetime.date(*map(int, raw_tick[0].split('-'))) ]
        result.extend( map(float, raw_tick[1:]) )
        return result

    def __iter__(self):
        for tick in self.data:
            yield tick

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def print_ticks(self, start, end):
        for tick in self.data[start:end]:
            print '{!s:4} {!s:8}'.format(tick.index, tick.close)


    def plot(self, *args):
        """ Save a plot of Tick args under the name symbol.png

        To get a plot of close, upper and lover bollinger band for N=30 and K=1
        for GOOG

        >>> Stock('GOOG').plot('close', 'upper_bb(30, 1)', 'lower_bb(30, 1)') #doctest: +SKIP
        """
        for value in args:
            match = re.match(r"(?P<method>\w+)(?P<parameters>\(.*\))?", value)
            dict_ = match.groupdict()
            method = dict_['method']
            parameters = None
            if dict_['parameters']:
                parameters = map(int, dict_['parameters'][1:-1].split(','))
            if parameters:
                plot([t.date for t in self],
                     [getattr(t, method)(*parameters) for t in self])
            else:
                plot([t.date for t in self],
                     [getattr(t, method) for t in self])
        savefig('png/{0}.png'.format(self.symbol))
        clf()