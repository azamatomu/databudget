import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

from formatters import (
    extract_product_name_from_index, add_emojis_to_products,
    price_formatter, price_with_date_formatter, change_formatter,
    format_dataframe
    )

import pygsheets
key_filename = 'telegram-bot-scoda.json'

import matplotlib
matplotlib.use('agg') # for no output

def load_sheet():

    gc = pygsheets.authorize(service_file=key_filename)
    sh = gc.open('prices-bishkek')
    data = sh.worksheets()
    working_data = [sheet for sheet in data if len(sheet.title.strip().replace('.', '')) == 8]

    prices_df = pd.concat([sheet.get_as_df() for sheet in working_data], ignore_index=True)
    prices_df['date'] = pd.to_datetime(prices_df['date'], format='%d-%m-%Y')
    products = prices_df['product'].unique()
    products.sort()
    products = add_emojis_to_products(list(products))
    

    product_choice = {i: col for i, col in enumerate(products)} 
    
    return prices_df, list(products), product_choice

def get_prices_for_last_date(prices_df):
    last_day_prices = (
        prices_df.groupby(['date', 'product'])['price'].mean()
        .to_frame().reset_index().set_index('date').groupby(['product']).last('1D')
        .sort_values('product')
    )
    last_day_prices_formatted = format_dataframe(last_day_prices, price_formatter, as_one=True)

    return last_day_prices_formatted # option 2


def get_product_price_history(prices_df, product_choice, i):
    product_name = extract_product_name_from_index(product_choice, i)

    tmp_df = prices_df[lambda df: df['product'] == product_name]
    tmp_df['date'] = tmp_df['date'].dt.strftime('%m-%d')
    
    over_time = tmp_df.sort_values('date').set_index('date')#.resample('1W')['price'].mean()
    plt.bar(over_time.index, over_time['price']) # over_time.plot()
    plt.title(f'Цена на {product_name}')
    plt.savefig(f'{i}.png')
    plt.close()
    over_time_formatted = format_dataframe(over_time[['product', 'price']], price_with_date_formatter, as_one=True)
    return over_time_formatted


def get_product_price_biggest_change_first_week(prices_df):
    n_weeks = len(prices_df['date'].unique())

    indexed_prices_df = prices_df.set_index(['date', 'product'])
    indexed_prices_df['price_first_week'] = indexed_prices_df.groupby(level="product").shift(n_weeks-1)['price']
    indexed_prices_df['dif_first_week'] = indexed_prices_df['price'] - indexed_prices_df['price_first_week']
    indexed_prices_df = indexed_prices_df.reset_index().set_index('date')

    first_week = indexed_prices_df.last('1D')[lambda df: df['dif_first_week'] != 0].sort_values('dif_first_week')
    first_week = first_week.reset_index()[['product', 'dif_first_week', 'price']].set_index('product')

    first_week_formatted = format_dataframe(first_week, change_formatter)
    return first_week_formatted

def get_product_price_biggest_change_last_week(prices_df):
    n_weeks = len(prices_df['date'].unique())

    indexed_prices_df = prices_df.set_index(['date', 'product'])
    indexed_prices_df['price_last_week'] = indexed_prices_df.groupby(level="product").shift(1)['price']
    indexed_prices_df['dif_last_week'] = indexed_prices_df['price'] - indexed_prices_df['price_last_week']
    indexed_prices_df = indexed_prices_df.reset_index().set_index('date')

    last_week = indexed_prices_df.last('1D')[lambda df: df['dif_last_week'] != 0].sort_values('dif_last_week')
    last_week = last_week.reset_index()[['product', 'dif_last_week', 'price']].set_index('product')

    last_week_formatted = format_dataframe(last_week, change_formatter)
    return last_week_formatted
    
