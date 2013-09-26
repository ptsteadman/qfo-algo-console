#!/usr/bin/python
#BEFO Key Stats Library -- Robert Cope 2013

from urllib import urlopen as uo
from bs4 import BeautifulSoup as bs
import html5lib
import math
import sys

class KeyStats:
	KeyStatsDict = {}
	def __init__(self, stock):
		self.BuildStatDict(stock)

	def StatsDict(self):
		return self.KeyStatsDict

	def BuildStatDict(self, stock):
		try:
			self.BuildProfileEntries(stock)
		except:
			print "Failed to load stock profile entries."
			print "Error:", sys.exc_info()[0]
			#raise
		try:
			self.BuildKeyStatEntries(stock)
		except:
			print "Failed to load stock key stat entries."
			print "Error:", sys.exc_info()[0]
			#raise #Don't worry about raising an error...lets not break our analysis just because my library is having a hard time.

	#Market Cap, %held by institutions, trailing annual dividend yield, debt/equity,
	def BuildProfileEntries(self, stock):
		pagesoup = bs(uo(self.generateProfileUrl(stock)))
		ProfileTable = pagesoup.findAll("table", {'class':"yfnc_datamodoutline1"})[0].findAll("table")[0]
		Entries = ProfileTable.findAll("tr")
		self.KeyStatsDict['Index'] = Entries[0].findAll('td')[1].text
		self.KeyStatsDict['Sector'] = Entries[1].findAll('td')[1].text
		self.KeyStatsDict['Industry'] = Entries[2].findAll('td')[1].text
		self.KeyStatsDict['Employees'] = Entries[3].findAll('td')[1].text
		
	
	def BuildKeyStatEntries(self, stock):
		pagesoup = bs(uo(self.generateKeyStatUrl(stock)))
		#Table 1: Valuation Measures		
		table1 = pagesoup.findAll("table", {'width':"100%", 'cellpadding':"2", 'cellspacing':"1", 'border':"0"})[0]
		table1rows = table1.findAll("tr")		
		self.KeyStatsDict['MarketCap'] = table1rows[0].findAll('td')[1].text
		self.KeyStatsDict['EnterpriseValue'] = table1rows[1].findAll('td')[1].text
		self.KeyStatsDict['TrailingPE'] = table1rows[2].findAll('td')[1].text
		self.KeyStatsDict['ForwardPE'] = table1rows[3].findAll('td')[1].text
		self.KeyStatsDict['PEGRatio'] = table1rows[4].findAll('td')[1].text
		self.KeyStatsDict['Prices/Sales'] = table1rows[5].findAll('td')[1].text
		self.KeyStatsDict['Prices/Book'] = table1rows[6].findAll('td')[1].text
		self.KeyStatsDict['Enterprise Value/Revenue'] = table1rows[7].findAll('td')[1].text
		self.KeyStatsDict['Enterprise Value/EBITDA'] = table1rows[8].findAll('td')[1].text
	
		#Table 6: Balance Sheet
		table6 = pagesoup.findAll("table", {'width':"100%", 'cellpadding':"2", 'cellspacing':"1", 'border':"0"})[5]
		table6rows = table1.findAll("tr")
		self.KeyStatsDict['Debt/Equity'] = table6rows[4].findAll('td')[1].text

		#Table 9: Share Statistics
		table9 = pagesoup.findAll("table", {'class':"yfnc_datamodoutline1", 'width':"100%", 'cellpadding':"0", 'cellspacing':"0", 'border':"0"})[8]
		table9rows = table9.findAll("tr")
		self.KeyStatsDict['PercentInsiders'] = table9rows[6].findAll('td')[1].text		
		self.KeyStatsDict['PercentInstitutions'] = table9rows[7].findAll('td')[1].text

		#Table 10: Dividends & Splits
		table10 = pagesoup.findAll("table", {'class':"yfnc_datamodoutline1", 'width':"100%", 'cellpadding':"0", 'cellspacing':"0", 'border':"0"})[9]
		table10rows = table10.findAll("tr")
		self.KeyStatsDict['FADY'] = table10rows[3].findAll('td')[1].text #Forward Annual Dividend Yield
		self.KeyStatsDict['TADY'] = table10rows[5].findAll('td')[1].text #Trailing Annual Dividend Yield

	def generateProfileUrl(self, stock):
		return 'http://finance.yahoo.com/q/pr?s='+stock+'+Profile'

	def generateKeyStatUrl(self, stock):
		return 'http://finance.yahoo.com/q/ks?s='+stock

	def __getitem__(self, key):
		return KeyStatsDict[key]

