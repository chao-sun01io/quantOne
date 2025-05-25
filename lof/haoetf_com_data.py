import requests
import pandas as pd
from datetime import datetime
from io import StringIO
import re

def clean_data(df):
    # Clean the DataFrame if necessary
    # trim whitespace from column names
    # and remove the spaces in column names
    
    df.columns = df.columns.str.replace(' ', '')

    # # For example, convert percentage strings to floats
    # if '实时溢价' in df.columns:
    #     df['实时溢价'] = pd.to_numeric(df['实时溢价'].str.rstrip('%'), errors='coerce') / 100.0
    
    # # Rename columns for consistency
    # df.rename(columns={'代码': 'code', '名称': 'name', '实时溢价': 'premium'}, inplace=True)
    return df

def fetch_lof_data():
    # URL for HAOETF LOF data
    url = "https://www.haoetf.com"
    
    # Headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        # Fetch the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse all tables from the webpage
        html_content = StringIO(response.text)
        tables = pd.read_html(html_content)
        
        # Usually the main LOF table is the first one
        if len(tables) > 0:
            df = tables[0]
            
            # Add timestamp from the `<p>数据更新时间：</p>`
            # Extract timestamp from the HTML using regex
            match = re.search(r'数据更新时间：([0-9\- :]+)', response.text)
            if match:
                update_time_str = match.group(1).strip()
                try:
                    update_time = datetime.strptime(update_time_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    update_time = datetime.now()
            else:
                update_time = datetime.now()
            df['update_time'] = update_time
            
            return clean_data(df)
        else:
            raise ValueError("No tables found on the webpage")
            
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

if __name__ == "__main__":
    # Fetch and display the data
    df = fetch_lof_data()
    if df is not None:
        print("Data columns:", df.columns)
        print("\nFirst few rows:")
        print(df.head())