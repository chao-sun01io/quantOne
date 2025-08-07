import requests
from datetime import datetime, timedelta
import akshare as ak
import pandas as pd
import os
"""
This script fetches the KWEB holdings data from the Kraneshares website,
retrieves the latest stock composite quotes from Sina Finance, and calculates the
interday NAV change based on the holdings and their respective prices.
"""


def get_last_trading_day():
    """
    Returns the last trading day as a string in the format MM_DD_YYYY.
    using pandas-market-calendar.
    """
    import pandas_market_calendars  as mcal
    nyse = mcal.get_calendar('NYSE')
    today = datetime.now().date()
    schedule = nyse.schedule(start_date=today - timedelta(days=30), end_date=today)
    # Find the last trading day before today
    last_trading_days = schedule.index[schedule.index.date < today]
    last_trading_day = last_trading_days[-1]
    return last_trading_day.strftime("%m_%d_%Y")  # Format: MM_DD_YYYY


def get_holdings(date_str=None):
    """
    Retrieves the holdings from the KWEB website.
    """
    if date_str is None:
        raise ValueError("date_str must be provided in the format MM_DD_YYYY")

    # e.g. https://kraneshares.com/csv/07_16_2025_kweb_holdings.csv
    base_url = "https://kraneshares.com/csv/"
    pcf_path = date_str + "_kweb_holdings.csv"

    if not os.path.exists(pcf_path):
        url = base_url + pcf_path
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            # Save the content to a file or process it directly
            with open(pcf_path, 'wb') as file:
                file.write(response.content)
    with open(pcf_path, 'r') as file:
        # Process the CSV file with pandas
        df = pd.read_csv(file, header=1)
        # keep only the relevant columns [Rank, Company Name, Ticker, % of Net Assets, Identifier]
        df.rename(columns={'% of Net Assets': 'Weight','Ticker': 'Symbol'}, inplace=True)
        df = df[['Company Name', 'Symbol', 'Weight', 'Identifier']]
        df['Weight'] = df['Weight'].astype(float) / 100.0

        # Data cleaning
        # remove row with Cash or cash in Company Name
        df = df[~df['Company Name'].str.contains('Cash', case =False, na=False)]
        # replace symbol 'YY' with 'JOYY'
        df['Symbol'] = df['Symbol'].replace('YY', 'JOYY')
        return df


def get_quotes_from_sina_us(symbols):
    """
    Retrieves the latest quotes for the given symbols from Sina Finance.
    """
    #example: https://hq.sinajs.cn/list=gb_pdd,gb_baba
    base_url = "https://hq.sinajs.cn/list="
    url = base_url + ",".join(["gb_" +  symbol.lower() for symbol in symbols])
    headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.text
#         data = """
# var hq_str_gb_pdd="拼多多,115.0400,3.03,2025-07-23 05:38:21,3.3800,112.8700,115.5650,111.4800,155.6700,87.1100,8596054,6313535,163316128988,9.91,11.610000,0.00,0.00,0.00,0.00,1419646462,0,115.2500,0.18,0.21,Jul 22 05:36PM EDT,Jul 22 04:00PM EDT,111.6600,129868,1,2025,982125285.0000,122.4613,109.4400,14939144.4509,115.0400,111.6600";
# var hq_str_gb_tme="腾讯音乐,21.3600,0.33,2025-07-23 05:35:22,0.0700,21.0200,21.4650,20.8800,22.5000,9.2300,5837059,6789086,33084600205,0.86,24.840000,0.00,0.00,0.18,0.00,1548904504,0,21.3700,0.05,0.01,Jul 22 05:21PM EDT,Jul 22 04:00PM EDT,21.2900,35050,1,2025,123955126.0000,21.4000,21.1100,748817.7440,21.3600,21.3000";
#  """
        # Parse the data
        # print(data)
        quotes = {}
        lines = data.split(';')
        for i, line in enumerate(lines):
            if line:
                parts = line.split(',')
                if  len(parts) < 3:
                    continue
                # Extract the symbol and price
                name = parts[0].split('=')[1].strip('"')
                price = float(parts[1])
                change = float(parts[2])
                # Extract the overnight price if available
                if len(parts) > 20:
                    overnight_price = float(parts[20])
                    overnight_change = float(parts[21])
                else:
                    # If overnight price is not available, set it to 0
                    overnight_price = 0.0
                    overnight_change = 0.0
                quotes[symbols[i]] = (name,price,change, overnight_price, overnight_change)
        return quotes

def get_quotes_from_sina_hk(symbols):
    """
    Retrieves the latest quotes for the given HK symbols from Sina Finance.
    """
    #example: https://hq.sinajs.cn/list=hk_00700
    base_url = "https://hq.sinajs.cn/list="
    # process symbols with '0' prefix
    hk_symbols = [f"{symbol:0>5}" for symbol in symbols]

    url = base_url + ",".join(["hk" + symbol for symbol in hk_symbols])
    headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn/",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.text
        # Parse the data
        """
                   0[0] = 0[1]     ,1      ,2      ,3      ,4      ,5      ,6(close),7     , 8(% change),9      ,10     ,11     ,12     ,13     ,14     ,15     ,16     ,17     ,18     ,19     ,20     ,21     ,22     ,23
        var hq_str_hk00700="TENCENT,腾讯控股,550.000,555.000,556.000,542.500,549.000,-6.000,-1.081,548.50000,549.00000,10639648067,19362555,0.000,0.000,560.000,345.980,2025/07/30,16:08";
        var hq_str_hk09988="BABA-W,阿里巴巴－Ｗ,117.700,120.700,119.600,117.100,117.100,-3.600,-2.983,117.10000,117.20000,10470600968,88754280,0.000,0.000,143.504,71.604,2025/07/30,16:08";
        """
        # print(data)
        quotes = {}
        lines = data.split(';')
        for i, line in enumerate(lines):
            if line:
                parts = line.split(',')
                if  len(parts) < 3:
                    continue
                # Extract the symbol and price
                name = parts[0].split('=')[1].strip('"')
                price = float(parts[6])
                change = float(parts[8])
                quotes[symbols[i]] = (name,price,change, 0,0)  # HK stocks do not have overnight price in this format
        return quotes

def get_quotes(holdings):
    """
    Retrieves the latest quotes for the given symbols.
    """
      # divide the holdings into US and HK stocks, alphabeta symbols are for US stocks and numbers are for HK stocks
    us_stocks = holdings[holdings['Symbol'].str.match('^[A-Za-z]+$')]['Symbol']
    hk_stocks = holdings[holdings['Symbol'].str.match('^\d+$')]['Symbol']
    symbols = us_stocks.tolist()
    current_price_us = get_quotes_from_sina_us(us_stocks.tolist())

    if not hk_stocks.empty:
        hk_symbols = hk_stocks.tolist()
        current_price_hk = get_quotes_from_sina_hk(hk_symbols)
        # print("Current Prices HK:", current_price_hk)

    # Combine US and HK quotes and make a DataFrame
    quotes = {}
    quotes.update(current_price_us)
    quotes.update(current_price_hk)
    composite_quotes = pd.DataFrame.from_dict(quotes, orient='index', columns=['Name','Price', '% Change', 'Overnight Price', '% Overnight Change'])
    composite_quotes.index.name = 'Symbol'
    composite_quotes.reset_index(inplace=True)
    composite_quotes['Price'] = composite_quotes['Price'].astype(float)
    composite_quotes['% Change'] = composite_quotes['% Change'].astype(float)
    composite_quotes['Overnight Price'] = composite_quotes['Overnight Price'].astype(float)
    composite_quotes['% Overnight Change'] = composite_quotes['% Overnight Change'].astype(float)

    return composite_quotes

def calculate_interday_change(composite_quotes, holdings):
    """
    Calculates the intraday change percentage.
    """
    # Merge the composite quotes with holdings on Symbol
    merged_df = pd.merge(holdings, composite_quotes, on='Symbol', how='left')
    
    print(merged_df[['Symbol', 'Weight', 'Price', '% Change']])
    # the sum of the weights multiplied by the % Change
    ichange = (merged_df['Weight'] * merged_df['% Change']/100.0).sum()

    print(f"Interday Nav Change: {ichange:.2%}")
    return ichange

if __name__ == "__main__":
    # Example usage
    holdings = get_holdings(get_last_trading_day())
    df = get_quotes(holdings)
    v = calculate_interday_change(df, holdings)
    
  