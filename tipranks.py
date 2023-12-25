
#Get rank of a ticker from tiprank.com uisng pure lxml
def get_tiprank_value(ticker):
    import requests
    from lxml import html

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
    }
    xpath_expression = '//*[@id="tr-stock-page-content"]/div[1]/div[4]/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div/div/div/div[1]/svg/text/tspan'
    
    # # Send an HTTP GET request to the URL
    url = f"https://www.tipranks.com/stocks/{ticker.lower()}"
    response = requests.get(url, headers=headers)

    elements = dict()    
    key = 'SmartScore'

    if response.status_code == 200:
        tree = html.fromstring(response.content)

        tspan_element = tree.find('.//tspan')
        if tspan_element is not None:
            tspan_element = tree.find('.//tspan', tspan_element)
            elements[key] = tspan_element.text
        else:
            print("tspan element not found.")
            elements[key]="-1"

    return elements



#Get rank and price target of a ticker from tiprank.com using beautifulsoup
def get_tiprank_values(ticker):

    from bs4 import BeautifulSoup
    import requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
    }

    # # Send an HTTP GET request to the URL
    url = f"https://www.tipranks.com/stocks/{ticker.lower()}"
    response = requests.get(url, headers=headers)

    elements = dict()    
    key = 'SmartScore'

    # key = list(xpathdict.keys())[0]

    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Use CSS selector to extract the value
        elements['AveragePriceTarget'] = float(soup.select_one('.colorblack.fonth10_semibold').text[1:])
        elements['SmartScore'] = int(soup.select_one('.w_pxsmall60.mxauto.fontWeightbold.fontSizelarge').text)

    return elements


###############################################################################
#Main Loop
###############################################################################

import pandas as pd
import requests
import time

#get ticker list by filtering only above 1 billion dollar company
DFUSA = pd.read_csv(r"\\192.168.1.1\New Volume\storage\premarket\america_2023-12-22.csv")[['Ticker','Price','Market Capitalization','Sector','Industry']]
# DFUSA = pd.read_csv('america_2023-09-16.csv')
tickerlst = list(DFUSA.query('`Market Capitalization`>1e6').Ticker)
print(f"Number of Tickers: {len(tickerlst)}")

# Main loop to retrieve profitability ranks for each ticker
dfs=[]
counter=0
for ticker in tickerlst:
    counter+=1
    print(f'{counter} out of {len(tickerlst)} {ticker}')
    # try:
    # Get profitability rank for the current ticker
    # value = "-1"
    # while value == "-1":
    #     valuedic = get_tiprank_value(ticker)
    #     value = valuedic['rank']

    time.sleep(30)  # Pause for 1 second
    # dftemp = pd.DataFrame(get_tiprank_value(ticker).values(), columns=['SmartScore'])    
    dftemp = pd.DataFrame([get_tiprank_values(ticker)])

    # Add the Ticker column for reference
    dftemp['Ticker'] = ticker
    dfs.append(dftemp)
    # except:
    #     print(f"could not retrieve data for {ticker}")
    #     pass

# Concatenate the DataFrames in the list to create a single DataFrame    
DFmerge = pd.concat(dfs, ignore_index=True)    
DFtotal = DFmerge.merge(DFUSA)

DFtotal['AveragePriceTarget_percent'] = 100 * (DFtotal['AveragePriceTarget'] - DFtotal['Price']) /DFtotal['Price']

DFtotal.to_csv('tipranks3.csv' , index=False)

DFtotal = pd.read_csv('tipranks3.csv')
DFtotal.query('`Market Capitalization`>1e9 & `SmartScore`>0').sort_values(by='SmartScore',ascending=True).head(20)

