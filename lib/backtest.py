from collections import namedtuple, Counter
import itertools
import math

from matplotlib.pyplot import plot, subplot2grid, ylim, yticks, savefig, clf, \
    fill_between


Trade = namedtuple('Trade', ['order', 'tick'])
Result = namedtuple('Result',['net','tick'])

class BackTest(object):
    """ Callable object running back tests for a strategy over a stock

    >>> backtest = BackTest()

    If goog is a Stock and bollinger a strategy (cf. strategy/__init__.py)

    >>> backtest(goog, bollinger) #doctest: +SKIP
    BackTest(trades=[99], position=short, gross=1253.63, net=662.1)

    Current position is short, gross PNL is 1253.63, net PNL taking into account
    the closing of the position and the trading costs if applicable is 662.1.

    Trading costs are 0 by default. To change that set the cost attribute of
    the backtest object to a function taking a trade as an argument and returning
    the cost.

    >>> backtest.cost = lambda trade: 0.5 * trade / 100
    >>> backtest #doctest: +SKIP
    BackTest(trades=[99], position=short, gross=1253.63, net=435.78005)
    """

    sell = {'long': None, None: 'short'}
    buy = {None: 'long', 'short': None}

    def __init__(self):
        self.cost = lambda trade: 0
        self.stock = None
        self.strategy = None
        self.trades = []

    def __call__(self, stock, strategy, startDate=0):
        self.stock = stock
        self.strategy = strategy
        self.trades = []
        self.startDate = startDate    #enter the start date in the format "YYYY-MM-DD" (including quotes).  must be trading day.
        if self.startDate != 0:
            self.startIndex = self.findIndex(self.stock, self.startDate)
        else:
            self.startIndex = 0
        for t in self.stock:
            if t.index >= self.startIndex:
                if strategy(t) == 'buy' and self.position != 'long':
                    self.trades.append(Trade('buy', t))
                elif strategy(t) == 'sell' and self.position != 'short':
                    self.trades.append(Trade('sell', t))
                elif strategy(t) == 'buyopen' and self.position != 'long':
                    self.trades.append(Trade('buyopen',t))
        return self

    def __repr__(self):
        return 'BackTest(trades=[{1}], net={0.net}, cumReturn={0.cumReturn}%, annuReturn={0.annualizedReturn}%)'.format(self, len(self.trades))
    
    def print_trades(self):
        self.oldNet = 0
        self.win = 0
        self.winarray = []
        print "ORDER     DATE    INDEX  CLOSE   UPBB   DWNBB"     
        for t in self.trades:
            self.win = Result(self._net(t.tick.index) - self.oldNet, t.tick)
            self.winarray.append(self.win)
            print '{!s:5}  {!s:9}  {!s:4}  {!s:7}  {!s:6}  {!s:6} | Net: {!s:7} Gain/Loss: {!s:6}'.format(t.order,t.tick.date,t.tick.index, round(t.tick.close,1),round(t.tick.upper_bb(30,1),1),round(t.tick.lower_bb(30,1),1),round(self._net(t.tick.index),1),round(self.win.net,1))
            self.oldNet = self._net(t.tick.index)
        print "\nCumulative Return: " + str(round(self.cumReturn,2)) + "%"
        print "Winning Trade Rate: " + str(self.computeWinLoss(self.winarray) * 100) + "%"
        print "Max Drawdown: " + str(self.maxDrawdown(self.winarray)['drawdown']) + "   Percent Loss:" + str(round((self.maxDrawdown(self.winarray)['drawdown']/ self.maxDrawdown(self.winarray)['tick'].close) * 100,2)) + "%\n"
        print "Days Elapsed: " + str(self.numDays())
        print "Annualized Return: " + str(self.annualizedReturn) + "%"
        return self
    
    def numDays(self):
        numtrades = len(self.stock) - 1
        daysElapsed = self.stock[numtrades].index - self.trades[0].tick.index
        return daysElapsed
    
    @property
    def annualizedReturn(self):
        exponent = (365.0 / self.numDays())
        if self.returnFactor < 0:
            returns = (math.pow(self.returnFactor*-1, exponent) - 1)*100 
            returns = round(returns,2)* -1 
        else:
            returns = (math.pow(self.returnFactor, exponent) - 1)*100 
            returns = round(returns,2)
        return returns

    @property
    def returnFactor(self):
        returnFactor = (self.net + self.trades[0].tick.close) / self.trades[0].tick.close
        return returnFactor

    def maxDrawdown(self, winarray):
        self.winarray = winarray
        self.drawdown = 0
        self.drawdowntick = 0
        for t in self.winarray:
            if t.net <= self.drawdown:
                self.drawdown = t.net
                self.drawdowntick = t.tick
        return { 'drawdown': self.drawdown, 'tick': self.drawdowntick }

    @property
    def cumReturn(self):
        self.cumReturns = round((((self.net + self.trades[0].tick.close)/ self.trades[0].tick.close) - 1) * 100,2) 
        return self.cumReturns

    def computeWinLoss(self, winarray):
        self.winarray = winarray
        self.wins = 0
        self.total = float(len(self.winarray))
        for t in self.winarray:
            if t.net >= 0:
                self.wins = self.wins + 1
        self.winRate = round(float(self.wins) / self.total,2)
        return self.winRate
      
    def findIndex(self, stock, date):
        self.stock = stock
        self.date = date
        found = False
        
        for t in stock:
            if str(t.date) == self.date:
                return t.index
        print "Date not found.  Is the date format \"YYYY-MM-DD\" (including quotes)?  Is date a trading day?"
        print "Strategy will run from earliest date.\n"

    @property
    def trade_cost(self):
        """ trade cost for the backtest period """
        return self._trade_cost(len(self.stock) - 1)

    def _trade_cost(self, tick_index):
        """ trade cost from start to tick_index """
        return sum(self.cost(abs(trade.tick.close)) for trade in self.trades
                   if trade.tick.index <= tick_index)

    @property
    def gross(self):
        """ gross pnl for the backtest period """
        return self._gross(len(self.stock) - 1)

    def _gross(self, tick_index):
        """ gross pnl from start to tick_index """
        #need to better understand the FOR IN IF and lambda
        sign = lambda trade: 1 if trade.order == 'sell' else -1
        sum = 0
        for trade in self.trades:
            if trade.tick.index <= tick_index:
                if trade.order == 'buyopen':
                    sum += (trade.tick.close - trade.tick.open)
                else:
                    sum += (sign(trade) * trade.tick.close)                   
        return sum

    @property
    def net(self):
        """ net pnl for the backtest period """
        return self._net(len(self.stock) - 1)

    def _net(self, tick_index):
        """ net pnl from start to tick_index """
        result = 0
        if self._position(tick_index) == 'long':
            result += self.stock[tick_index].close
        elif self._position(tick_index) == 'short':
            result -= self.stock[tick_index].close
        result += self._gross(tick_index)
        result -= self._trade_cost(tick_index)
        return result

    @property
    def position(self):
        """ position at the end of the backtest period """
        return self._position(len(self.stock) - 1)

    def _position(self, tick_index, numeric_flag=False):
        """ position at tick_index 1/0/-1 if numeric_flag """
        position_ = {1: 'long', 0: None, -1: 'short'}
        counter = Counter(trade.order for trade in self.trades
                          if trade.tick.index <= tick_index)
        numeric = counter['buy'] - counter['sell']
        if numeric_flag:
            return numeric
        return position_[counter['buy'] - counter['sell']]

    def plot(self):
        date = [tick.date for tick in self.stock]
        net = [self._net(tick.index) for tick in self.stock]
        position = [self._position(tick.index, True) for tick in self.stock]
        plot_net = subplot2grid((3, 1), (0, 0), rowspan=2)
        plot(date, net)
        plot_position = subplot2grid((3, 1), (2, 0), sharex=plot_net)
        ylim(-1.5, 1.5)
        yticks((-1, 0, 1), ('short', '...', 'long'))
        fill_between(date, position)
        savefig('png\{0}_{1}.png'.format(self.stock.symbol,
                                     self.strategy.__class__.__name__))
        clf()
	
		