import os
import pandas as pd
import datetime as dt
from datetime import datetime
import requests

#Alpha Vantage API

alpha_key = os.environ.get('ALPHAVANTAGE_KEY')

def get_ticker_data_avd(ticker):
    url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={ticker}&market=USD&apikey={alpha_key}"
    r = requests.get(url)
    data = r.json()
    try:
        df = pd.DataFrame(data)
    except Exception:
        print("Invalid crypto ticker")
        return None
    df = df.iloc[7:]
    df = df.drop(['Meta Data'], axis = 1)
    df.reset_index()
    price = ticker+' Closing price'
    time = ticker+' Date'
    df_new = pd.DataFrame()
    prices_list = []
    time_list = []
    for i in range(len(df.index)):
        prices_list.append(df['Time Series (Digital Currency Daily)'][i]['4b. close (USD)'])
        time_list.append(df.index[i])
    df_new = df_new.assign(price = prices_list)
    df_new = df_new.assign(time = time_list)
    df_new = df_new.rename(columns = {'price': price, 'time': time})
    return df_new

def date_split(date):
    #input is in the form of '2020-04-27'
    date = date.split('-')
    next_date = dt.date(int(date[0]), int(date[1]), int(date[2]))
    return next_date

def date_string(date):
    #input is a datetime object
    return date.strftime("%Y-%m-%d")

def get_start_date(ticker, df):
    #gets the first monday
    bool = True
    i = 0
    initial = df[ticker+' Date'][len(df)-1].split("-")
    if dt.datetime.today().year - int(initial[0]) < 2 or dt.datetime.today().month > int(initial[1]):
        bool = False
        print("2 years of data not available for this ticker")
        return None
    while bool:
        start_date = df[ticker+' Date'][i]
        date_list = start_date.split('-')
        if dt.date(int(date_list[0]), int(date_list[1]), int(date_list[2])).weekday() == 0:
            bool = False
            print(start_date)
            return start_date
        else:
            i += 1


def get_weekly_data(df, start_date, ticker):
    df_week = pd.DataFrame()
    test_list = []
    next_date = start_date
    test_list.append(next_date)
    while date_split(df[ticker+' Date'][len(df)-1]) <= date_split(next_date):
        next_date = date_split(next_date) - dt.timedelta(days = 7)
        next_date = date_string(next_date)
        test_list.append(next_date)

    test_list.pop(-1)
    for i in range(len(test_list)):
        df_week = df_week.append(df.loc[df[ticker+' Date'] == test_list[i]])
    price = ticker+' Closing price'
    time = ticker+' Date'
    df_week = df_week.rename(columns = {'Close': price, 'Date': time})
    df_week = df_week.reset_index(drop = True)
    return df_week


def get_crypto_inputs():
    number = input() # max 5
    number = int(number)
    ticker_list = []
    for i in range(1, number+1):
        ticker_list.append(input())
        i += 1
    return ticker_list


def get_crypto_data(ticker_list):
    if ticker_list == []:
        return 
    df_final = pd.DataFrame()
    for i in range(len(ticker_list)):
        df = get_ticker_data_avd(ticker_list[i])
        sd = get_start_date(ticker_list[i], df)
        if df.empty or sd is None:
            print("Something went wrong")
            break
        else:
            df_week = get_weekly_data(df, sd, ticker_list[i])
        df_final = pd.concat([df_final, df_week], axis = 1)
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
    df_final = df_final.iloc[:104]
    df_final = df_final.loc[::-1].reset_index(drop = True) #reverses all the rows
    df_final = df_final.reset_index(drop = True)
    return df_final

def c_turn_to_csv(df):
    df.to_csv('crypto.csv', index = False)