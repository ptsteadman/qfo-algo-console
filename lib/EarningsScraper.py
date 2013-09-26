#!/usr/bin/python

from urllib import urlopen
from lib import Stock
from bs4 import BeautifulSoup as bs
import csv
import sys
import urllib2
import os
import datetime



class EarningsScraper:

	def __init__(self, writeFile):
		self.companies = dict()
		self.writeFile = writeFile
	
	#def getCompanies():
		#return companies.values()
	
	@staticmethod
	def generateUrl(date = 'today'):
		baseURL = 'http://biz.yahoo.com'
		return baseURL + '/research/earncal/' + str(date) + '.html'
		

	def scrapeDateRange(self,startDate, endDate, writeFile=False):
		d1 = datetime.date(int(str(startDate)[0:4]),int(str(startDate)[5:7]),int(str(startDate)[8:10]))
		d2 = datetime.date(int(str(endDate)[0:4]),int(str(endDate)[5:7]),int(str(endDate)[8:10]))
		diff = d2 - d1
		for d in range(diff.days + 1):
			dateToScrape = d1 + datetime.timedelta(days=d)			
			self.scrapeEarnings(int(dateToScrape.year)*10000 + int(dateToScrape.month)*100 + int(dateToScrape.day))
		return self.companies
	
	def scrapeEarnings(self,date, writeFile = False):
		companies = []
		outputf = 'csv/' + str(date) + '.csv' #----------------------------------------------- FILE NAME --------------------------------------
		print date
		formattedDate = datetime.date(int(str(date)[0:4]),int(str(date)[4:6]),int(str(date)[6:8]))
		if writeFile:
			if (os.path.exists(outputf)):
				os.remove(outputf)
			csvfile = open(outputf, 'wb')
			DATACSV = csv.writer(csvfile)
		dataURL = EarningsScraper.generateUrl(date)
		dataPage = urlopen(dataURL)
		tbIndex = 6
		soup = bs(dataPage)
		#begin saving rows
		count = 0
		tbls = soup.findAll("table") #, cellpadding=2, cellspacing=0, border=0, width='100%')[3]
		print len(tbls)-1
		print tbIndex
		table = tbls[tbIndex]
		rows = table.findAll('tr')
		rowToWrite=[]
		for r in rows:
			count = count + 1
			rowToWrite=[]
			columns = r.findAll('td')
			for c in columns:
				print (c.text).encode('ascii', 'ignore')
				rowToWrite.append((c.text).encode('ascii', 'ignore').strip())
			print rowToWrite
			if count > 2 and count < len(rows):
				name = rowToWrite[0] #set the company name
				tkr = rowToWrite[1] #set the company ticker
				releaseTime = rowToWrite[2] #set the announced company release time
				if (tkr not in companies and EarningsScraper.isSuitable(tkr, releaseTime)):
					if releaseTime == 'Before Market Open':
						c = Stock(symbol=tkr, earnings=formattedDate)
						self.companies[tkr] = c
					if releaseTime == 'After Market Close':
						if formattedDate.weekday == 4:
							c = Stock(symbol=tkr, earnings=(formattedDate + datetime.timedelta(3)))
							self.companies[tkr] = c
						else:
							c = Stock(symbol=tkr, earnings=(formattedDate + datetime.timedelta(1)))
							self.companies[tkr] = c
			if writeFile:
				DATACSV.writerow(rowToWrite)
		if writeFile:
			csvfile.close()
	
	@staticmethod
	def isSuitable(tkr, rTime):
		if not tkr.isalpha():
			return False
		if not len(tkr) < 5:
			return False
		if not (rTime == 'Before Market Open' or rTime == 'After Market Close'):
			return False
		return True

	@staticmethod
	def write_summary(companies, fname='defaultName'):
		outputf = 'csv/' + str(fname) + '.csv'
		if (os.path.exists(outputf)):
				os.remove(outputf)
		csvfile = open(outputf, 'wb')
		wrtr = csv.writer(csvfile)
		wrtr.writerow(['ticker', 'DaysPriorPerformance', 'DaysPriorSpyPerformance', 'DaysPriorAvgVolume', 'DayOfPerformance', 'DayOfVolume', 'DayOfMarketPerformance', 'ClosePositionRatio', 'DaysAfterPerformance', 'DaysAfterSpyPerformance', 'DaysAfterAvgVolume'])
		wrtr.writerow("")
		for key, value in companies.items():
			summary = value.return_summary_dict()
			print 'Processing:' + summary['ticker']
			wrtr.writerow([summary['ticker'], summary['DaysPriorPerformance'], summary['DaysPriorSpyPerformance'], summary['DaysPriorAvgVolume'], summary['DayOfPerformance'], summary['DayOfVolume'], summary['DayOfMarketPerformance'], summary['ClosePositionRatio'], summary['DaysAfterPerformance'], summary['DaysAfterSpyPerformance'], summary['DaysAfterAvgVolume']])
			
			
		
		
		
	