# %%
# start as a bot to keep track of lof premium and discoun

# %%
import haoetf_com_data
import palmmicro_com_data
import pandas as pd
# %% 
# Get the latest data of LOF spot
# df = ak.fund_lof_spot_em()
# print(df.info())
# # query 161128 from symbol and print
# df[df['代码'] == '161128']


# %%
# Get the latest data from haoetf.com
lof = haoetf_com_data.fetch_lof_data()
## filter the premium that is greater than the threshold
threshold = 0.5 # 0.1%
# Convert '实时溢价' from percentage string to float
lof['实时溢价'] = pd.to_numeric(lof['实时溢价'].str.rstrip('%'),errors='coerce')
lof = lof[lof['实时溢价'] > threshold]
## print the result
print(lof[['代码', '名称', '实时溢价','update_time']])

# %%
# Get the latest data from palmmicro.com
lof =  palmmicro_com_data.fetch_lof_data()
# Convert '实时溢价' from percentage string to float
lof['实时溢价'] = pd.to_numeric(lof['实时溢价'].str.rstrip('%'), errors='coerce')
lof = lof[lof['实时溢价'] > threshold]
## print the result
print(lof[['代码', '名称', '实时溢价','update_time']])
