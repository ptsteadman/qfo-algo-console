#!/usr/bin/env python
# encoding: utf-8

import code

from lib import Stock, BackTest, Basket, csvOut, EarningsScraper, StockKeyStatLib
from strategy import Bollinger, Monkey, Pairs, Buy, Short, RSI, BasicGap, ChinaGap
import datetime

banner = """BEFO STRATEGY BACKTESTING CONSOLE
---------------------------------------------------
-Instantiate Tick File Object: goog = Stock('GOOG')
-Instantiate Backtest Object: backtest = BackTest()
-Define Parameters for Strategy: bollinger = Bollinger(30, 1)
-Run Backtest: backtest(goog, bollinger)
-Plot Backtest in .png File: backtest.plot()
---------------------------------------------------"""

backtest = BackTest()
buy = Buy()
#basket = Basket('test.txt')
revBB = Bollinger(30,1)
breakBB = Bollinger(30,1,"breakout")
scraper = EarningsScraper(True)
'''march12 = scraper.scrapeDateRange("2013-03-12","2013-03-12")'''
'''
goog = Stock("GOOG")
hsi = Stock("^HSI")
vix = Stock("VXX")
sha = Stock("000001.SS")
vixstrat = Pairs(vix,30,1)
bollinger = Bollinger(30,1)
short = Short()
'''

code.interact(banner=banner, local=locals())
