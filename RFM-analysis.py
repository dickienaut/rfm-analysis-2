# MIT License
#
# Copyright (c) [2018] [Murat Ova]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#!/usr/bin/python

import sys, getopt
import pandas as pd
from datetime import datetime

def main(argv):
   inputfile = ''
   outputfile = ''
   inputdate = ''

   try:
      opts, args = getopt.getopt(argv,"hi:o:d:")
   except getopt.GetoptError:
      print 'RFM-analysis.py -i <orders.csv> -o <rfm-table.csv> -d <yyyy-mm-dd>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'RFM-analysis.py -i <orders.csv> -o <rfm-table.csv> -d "yyyy-mm-dd"'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg   
      elif opt in ("-d", "--dinputdate"):
         inputdate = arg  

   rfm(inputfile,outputfile,inputdate)


def rfm(inputfile, outputfile, inputdate):
   print " "
   print "---------------------------------------------"
   print " Calculating RFM segmentation for " + inputdate
   print "---------------------------------------------"

   NOW = datetime.strptime(inputdate, "%Y-%m-%d")

   # Open orders file
   orders = pd.read_csv(inputfile, sep=',')
   orders['order_date'] = pd.to_datetime(orders['order_date'])
   
   rfmTable = orders.groupby('customer').agg({'order_date': lambda x: (NOW - x.max()).days, # Recency
                                              'order_id': lambda x: len(x),      # Frequency
                                              'grand_total': lambda x: x.sum()}) # Monetary Value

   rfmTable['order_date'] = rfmTable['order_date'].astype(int)
   rfmTable.rename(columns={'order_date': 'recency', 
                              'order_id': 'frequency', 
                              'grand_total': 'monetary_value'}, inplace=True)


   quantiles = rfmTable.quantile(q=[0.25,0.5,0.75])
   quantiles = quantiles.to_dict()

   rfmSegmentation = rfmTable

   rfmSegmentation['R_Quartile'] = rfmSegmentation['recency'].apply(RClass, args=('recency',quantiles,))
   rfmSegmentation['F_Quartile'] = rfmSegmentation['frequency'].apply(FMClass, args=('frequency',quantiles,))
   rfmSegmentation['M_Quartile'] = rfmSegmentation['monetary_value'].apply(FMClass, args=('monetary_value',quantiles,))

   rfmSegmentation['RFMClass'] = rfmSegmentation.R_Quartile.map(str) + rfmSegmentation.F_Quartile.map(str) + rfmSegmentation.M_Quartile.map(str)

   rfmSegmentation.to_csv(outputfile, sep=',')

   print " "
   print " DONE! Check %s" % (outputfile)
   print " "

# We create two classes for the RFM segmentation since, being high recency is bad, while high frequency and monetary value is good. 
# Arguments (x = value, p = recency, monetary_value, frequency, k = quartiles dict)
def RClass(x,p,d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]: 
        return 3
    else:
        return 4
    
# Arguments (x = value, p = recency, monetary_value, frequency, k = quartiles dict)
def FMClass(x,p,d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]: 
        return 2
    else:
        return 1



if __name__ == "__main__":
   main(sys.argv[1:])
