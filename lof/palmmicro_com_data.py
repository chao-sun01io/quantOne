from io import StringIO
import requests
import pandas as pd

def fetch_lof_data():
    url = "https://palmmicro.com/woody/res/lofcn.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    response = requests.get(url,headers = headers)
    response.raise_for_status()
    
    html_content = StringIO(response.text)
    tables = pd.read_html(html_content)

    if len(tables) >= 2:
        if '日期' in tables[2].columns:
            tables[2] = tables[2].drop(columns=['日期'])

        # Merge the first two tables on '代码'
        df = pd.merge(tables[1], tables[2], on='代码', how='outer')

        # Add a timestamp column
        df['update_time'] = pd.Timestamp.now()
        df = clean_data(df)
    else:
        raise ValueError("No tables found on the webpage")
    
    return df

def clean_data(df):
    cols = list(df.columns)

    # Move '代码' to the second position if it exists
    if '代码' in cols and '名称' in cols:
        cols.remove('名称')
        code_idx = cols.index('代码')
        cols.insert(code_idx + 1, '名称')
        df = df[cols]
    # Rename '溢价.1' to '实时溢价' if it exists
    if '溢价.1' in df.columns:
        df.rename(columns={'溢价.1': '实时溢价'}, inplace=True)

    return df

if __name__ == "__main__":
    lof_data = fetch_lof_data()
    print(lof_data.columns.to_list())
    print(lof_data.head())