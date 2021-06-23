import sys
import os
import pandas as pd

sys.path.append('D:\work')

from stonks.stock_api import *
from stonks.crypto_api import *


alpha_key = os.environ.get('ALPHAVANTAGE_KEY')

def append_c_s(crypto_df, stock_df):
    final_df = pd.concat([crypto_df, stock_df], axis = 1)
    final_df = final_df.loc[:,~final_df.columns.duplicated()]
    cols = final_df.columns.tolist()
    #index = final_df.columns.get_loc('Date')
    cols.append('Date')
    cols.remove('Date')
    final_df = final_df[cols]
    return final_df

def run_():
    stock_input = get_stock_inputs()
    crypto_input = get_crypto_inputs()

    stock_df = get_stock_data(stock_input)
    crypto_df = get_crypto_data(crypto_input)

    df_final = append_c_s(crypto_df, stock_df)
    df_final.to_csv('final.csv', index = False)    

if __name__ == "__main__":
    run_()

