#pip install yfinance
import yfinance as yf
import pandas as pd
import datetime as dt
import numpy as np

def get_ticker():
    return input()

def get_ticker_data(ticker):
    the_ticker = yf.Ticker(ticker)
    hist = the_ticker.history(period="2y")
    hist = hist.reset_index()
    #type(hist) #pandas dataframe
    df_Stock = pd.DataFrame()
    df_Stock = df_Stock.assign(Close = hist['Close'].values)
    df_Stock = df_Stock.assign(Date = hist['Date'].values)
    return df_Stock

def date_split(date):
    #input is in the form of '2020-04-27'
    date = date.split('-')
    next_date = dt.date(int(date[0]), int(date[1]), int(date[2]))
    return next_date

def date_string(date):
    #input is a datetime object
    return date.strftime("%Y-%m-%d")

def get_start_date(df):
    #gets the first monday
    bool = True
    i = 0
    while bool:
        start_date = date_string(df['Date'][i])
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
    while df['Date'][len(df)-1] >= date_split(next_date):
        next_date = date_split(next_date) + dt.timedelta(days = 7)
        next_date = date_string(next_date)
        test_list.append(next_date)

    test_list.pop(-1)
    for i in range(len(test_list)):
        df_week = df_week.append(df.loc[df['Date'] == test_list[i]])
    price = ticker+' Closing price'
    time = ticker+' Date'
    df_week = df_week.rename(columns = {'Close': price, 'Date': time})
    return df_week

def get_stock_inputs():
    number = input() # max idk
    number = int(number)
    ticker_list = []
    for i in range(1, number+1):
        ticker_list.append(input())
        i += 1
    return ticker_list

def get_stock_data(ticker_list):
    df_final = pd.DataFrame()
    for i in range(len(ticker_list)):
        try:
            data = get_ticker_data(ticker_list[i])
            date1 = get_start_date(data)
            df = get_weekly_data(data, date1, ticker_list[i])
        except (KeyError, IndexError) as e:
            continue
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


def s_turn_to_csv(df):
    df.to_csv('stock.csv', index = False)

#test implementation
test = get_stock_inputs()
df = get_stock_data(test)
s_turn_to_csv(df)

#random_ticker implementation
datapath = f"D://work/stonks/random_tickers.csv"
data = pd.read_csv(datapath)
the_list = data.values.tolist()
list_ = []
for i in range(len(the_list)):
    list_.append(the_list[i][0])
tickers_df = get_stock_data(list_)
s_turn_to_csv(tickers_df)
