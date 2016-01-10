__author__ = 'david'


from pandas_datareader import data, wb
#import wbdata
import pandas
import matplotlib.pyplot as plt

# #set up the countries I want
# countries = ["CL","UY","HU"]
#
# #set up the indicator I want (just build up the dict if you want more than one)
# indicators = {'SP.DYN.LE00.IN':'Life expectancy at birth, total (years)'}
#
# #grab indicators above for countires above and load into data frame
# df = wbdata.get_dataframe(indicators, convert_date=False)
# #wbdata.get_dataframe
# #df is "pivoted", pandas' unstack fucntion helps reshape it into something plottable
# dfu = df.unstack(level=0)
#
# # a simple matplotlib plot with legend, labels and a title
# dfu.plot();
# plt.legend(loc='best');
# plt.title("GNI Per Capita ($USD, Atlas Method)");
# plt.xlabel('Date'); plt.ylabel('GNI Per Capita ($USD, Atlas Method');


ind = ['SP.DYN.LE00.IN']
#countries = ['iso2c']
dat = wb.download(indicator=ind, country='all', start=2013, end=2013).dropna()
dat.columns = ['cellphone']
print(dat)