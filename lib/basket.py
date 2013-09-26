import itertools
import math
from lib import Stock, BackTest
from datetime import date

class Basket(object):
    """ the basket object allows the user to backtest a strategy over a list of stocks, 
    and view performance data for the basket as a whole, or view a ranking of different 
    stocks.  the basket can be loaded from a .txt file and then used with different strategies.
    loading a basket list will identify the latest start date and use it for all backtests.

    examples:

    chineseStocks = Basket(chineseStocks.txt)
    """
    #backtestArray = dict() #dictionary of stocks and backtests

    def __init__(self, path):
        self.path = path

        with open('baskets/' + self.path, 'r') as f:
            read_data = f.read()
        self.symbolArray = read_data.split('\n')
        print self.symbolArray
        self.backtestArray = dict()
        for symbol in self.symbolArray:
            self.backtestArray.update({symbol : (Stock(symbol),BackTest())})

    def findLatestDate(self, stockArray):
        latestDate = date.min
        for key in stockArray.keys():
            testDate = stockArray.get(key)[0][0].date
            if testDate >= latestDate:
                latestDate = testDate
        return str(latestDate)

    def fetch(self, symbol):
        return self.backtestArray.get(symbol)[1]

    def __call__(self, strategy):
        self.strategy = strategy
        self.resultsArray = []
        for key in self.backtestArray.keys():  
            self.backtestArray.get(key)[1](self.backtestArray.get(key)[0],self.strategy, self.findLatestDate(self.backtestArray))  # actually run backtest 
            print "Finished " + key + "..." 
        for key in self.backtestArray.keys():
            self.resultsArray.append(self.backtestArray.get(key))
        self.resultsArray.sort(key = lambda tup : tup[1].cumReturn, reverse = True)
        i = 1
        print "RESULTS:"
        for result in self.resultsArray:
            print '{!s:4} {!s:6}  '.format(i, result[0].symbol) + str(result[1])
            i = i + 1  
        