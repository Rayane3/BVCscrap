import requests 
from bs4 import BeautifulSoup
import pandas as pd
import json
import datetime
from .utils import *

def loadata(name, start=None,end=None,decode="utf-8"):
	"""
	Load Data 
	Inputs: 
			Input   | Type                             | Description
			=================================================================================
			 name   |string                            | You must respect the notation. To see the notation see BVCscrap.notation()
	         start  |string "YYYY-MM-DD"               | starting date Must respect the notation
	         end    |string "YYYY-MM-DD"               | Must respect the notation
	         decode |string                            | type of decoder. default value is utf-8. If it is not working use utf-8-sig
	Outputs:
	        Output | Type                             | Description
	       ================================================================================= 
	               | pandas.DataFrame (4 columns)     |Value	Min	Max	Variation	Volume
	"""
	code = get_code(name)
	if not code and name not in ["MASI", "MSI20"]:
		raise ValueError(f"Unknown name or missing ISIN for: {name}")

	if name not in ["MASI", "MSI20"]:
		if not start or not end:
			start = '2011-09-18'
			end = str(datetime.datetime.today().date())

		link = f"https://medias24.com/content/api?method=getPriceHistory&ISIN={code}&format=json&from={start}&to={end}"
	else:
		if name == "MASI":
			link = "https://medias24.com/content/api?method=getMasiHistory&periode=10y&format=json"
		else:
			link = "https://medias24.com/content/api?method=getIndexHistory&ISIN=msi20&periode=10y&format=json"

	request_data = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})

	if request_data.status_code != 200 or not request_data.text.strip().startswith('{'):
		raise ValueError(f"Bad API response for {name}: {request_data.status_code}, body={request_data.text[:150]}")

	data = get_data(request_data.text, decode)

	if name in ["MASI", "MSI20"] and start and end:
		data = produce_data(data, start, end)

	return data


def loadmany(*args,start=None,end=None,feature="Value",decode="utf-8"):
	"""
	Load the data of many equities  
	Inputs: 
			Input   | Type                             | Description
			=================================================================================
			 *args  |strings                           | You must respect the notation. To see the notation see BVCscrap.notation
	         start  |string "YYYY-MM-DD"               | starting date Must respect the notation
	         end    |string "YYYY-MM-DD"               | Must respect the notation
	         feature|string                            | Variable : Value,Min,Max,Variation or Volume
	         decode |string                            | type of decoder. default value is utf-8. If it is not working use utf-8-sig
	Outputs:
	        Output | Type                                 | Description
	       ================================================================================= 
	               | pandas.DataFrame (len(args) columns) | close prices of selected equities
	"""
	if type(args[0])==list:
		args=args[0]
	data=pd.DataFrame(columns=args)
	for stock in args:
		value=loadata(stock,start,end,decode)
		data[stock]=value[feature]
	return data


def getIntraday(name,decode="utf-8"):
    """
    Load intraday data
    Inputs: 
        -Name: stock,index 
        -decode: default value is "utf-8", if it is not working use : "utf-8-sig"
    
    """
    if name != "MASI" and name != "MSI20":
        code=get_code(name)
        link="https://medias24.com/content/api?method=getStockIntraday&ISIN="+code+"&format=json"
    elif name == "MASI":
            link="https://medias24.com/content/api?method=getMarketIntraday&format=json"
    else :
            link="https://medias24.com/content/api?method=getIndexIntraday&ISIN=msi20&format=json"
    request_data = requests.get(link,headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(request_data.text,features="lxml")
    data=intradata(soup,decode)
    return data
