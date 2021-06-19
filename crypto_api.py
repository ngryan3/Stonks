import os
from coinbase.wallet.client import Client
import cbpro
import json
import pandas as pd
import datetime as dt
from datetime import datetime
import requests
#pip install coinbase
coinbase_client_id= os.environ.get('COINBASE_CLIENT_ID')
coinbase_secret_id= os.environ.get('COINBASE_SECRET_ID')

client = Client(coinbase_client_id, coinbase_secret_id)

def get_ticker():
    return input()

def get_ticker_data(ticker):
    data_object = client.get_historic_prices(currency_pair = ticker+'-USD', period = 'all')
    data_json = json.dumps(data_object)
    df = pd.read_json(data_json)
    prices_list = []
    time_list = []
    for i in range(len(df['prices'])):
        prices_list.append(df['prices'][i]['price'])
        raw = df['prices'][i]['time']
        raw = raw.split('T')
        date_time_ = raw[0]
        time_list.append(date_time_)
    df = df.assign(price = prices_list)
    df = df.assign(time = time_list)
    df.pop("prices")
    return df

def get_start_date(df):
    #gets the first monday
    bool = True
    i = -1
    while bool:
        start_date = df['time'][len(df)+i]
        date_list = start_date.split('-')
        if dt.date(int(date_list[0]), int(date_list[1]), int(date_list[2])).weekday() == 0:
            bool = False
            print(start_date)
            return start_date
        else:
            i -= 1

def date_split(date):
    #input is in the form of '2020-04-27'
    date = date.split('-')
    next_date = dt.date(int(date[0]), int(date[1]), int(date[2]))
    return next_date

def date_string(date):
    #input is a datetime object
    return date.strftime("%Y-%m-%d")


def get_weekly_data(df, start_date):
    df_week = pd.DataFrame()
    test_list = []
    next_date = start_date
    test_list.append(next_date)
    while date_split(df['time'][0]) >= date_split(next_date):
        next_date = date_split(next_date) + dt.timedelta(days = 7)
        next_date = date_string(next_date)
        test_list.append(next_date)

    test_list.pop(-1)
    for i in range(len(test_list)):
        df_week = df_week.append(df.loc[df['time'] == test_list[i]])
    return df_week


def turn_to_csv(ticker, df):
    df.to_csv(ticker+'.csv')


#Alpha Vantage API

alpha_key = os.environ.get('ALPHAVANTAGE_KEY')

def get_ticker_data_av(ticker):
    url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_WEEKLY&symbol={ticker}&market=USD&apikey={alpha_key}"
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data)
    df = df.iloc[7:]
    df = df.drop(['Meta Data'], axis = 1)
    df.reset_index()
    price = ticker+' Closing price'
    time = ticker+' Date'
    df_new = pd.DataFrame()
    prices_list = []
    time_list = []
    for i in range(len(df.index)):
        prices_list.append(df['Time Series (Digital Currency Weekly)'][i]['4b. close (USD)'])
        time_list.append(df.index[i])
    df_new = df_new.assign(price = prices_list)
    df_new = df_new.assign(time = time_list)
    df_new = df_new.rename(columns = {'price': price, 'time': time})
    return df_new


def get_crypto_inputs():
    number = input() # max 5
    number = int(number)
    ticker_list = []
    for i in range(1, number+1):
        ticker_list.append(input())
        i += 1
    return ticker_list


def get_crypto_data(ticker_list):
    df_final = pd.DataFrame()
    for i in range(len(ticker_list)):
        df = get_ticker_data_av(ticker_list[i])
        df_final = pd.concat([df_final, df], axis = 1)
        if i != 0:
            #print(df_final[ticker_list[i]+' Date'].tolist() == df_final[ticker_list[0]+' Date'].tolist())
            if df_final[ticker_list[i]+' Date'].tolist() == df_final[ticker_list[0]+' Date'].tolist():
                df_final = df_final.drop(ticker_list[i]+ ' Date', axis = 1)
    cols = df_final.columns.tolist()
    index = cols[1]
    cols.remove(ticker_list[0]+' Date')
    cols.append(index)
    df_final = df_final[cols]
    df_final = df_final.rename(columns={ticker_list[0]+' Date': 'Date'})
    return df_final


def c_turn_to_csv(df):
    df.to_csv('crypto.csv', index = False)

#test implementation
test = get_crypto_inputs()
df = get_crypto_data(test)
c_turn_to_csv(df)