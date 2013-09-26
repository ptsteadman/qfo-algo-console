import csv
from lib import Stock

class csvOut(object):

    def __init__(self, toCsv):
        self.toCsv = toCsv
        self.fileName = str(toCsv.symbol) + ".csv"
        write(self.toCsv)

    def write(self, toCsv):  
        with open(self.fileName, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in toCsv:
                writer.writerow([row.date] + [row.close])







