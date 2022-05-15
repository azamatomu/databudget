import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate


import pygsheets
key_filename = 'telegram-bot-scoda.json'

import matplotlib
matplotlib.use('agg') # for no output

e_rocket = "\U0001f680"
e_money = "\U0001f4b8"
e_rise = "\U0001F4C8"
e_fall = "\U0001F4C9"
e_egg = "\U0001F95A" 
e_potato = "\U0001F954"
emoji_products = [e_egg, e_potato]
emoji_mappings = {e_egg: 'Яйца',
                  e_potato: 'Картофель'}

def add_emojis_to_products(products):
    return products + emoji_products

def extract_product_name_from_index(product_choice, i):
    product_name = product_choice[i]
    if product_name in emoji_products: 
        mapped_product_name = emoji_mappings[product_name]

        return mapped_product_name
    else:
        return product_name

def price_formatter(list_to_format):
    # product, price = x[0], x[1]
    formatted = [f'{x[0]}: {e_money}{x[1]}' for x in list_to_format]
    return formatted

def price_with_date_formatter(list_to_format):
    # date, price = x[0], x[2]
    formatted = [f'{x[0]}: {e_money}{x[2]}' for x in list_to_format]
    return formatted


def change_formatter(list_to_format):
    formatted = []
    is_positive, is_negative = False, False
    for x in list_to_format:
        # if (difference > 0) != is_positive:

        
        product, amount, difference = x[0], int(x[2]), int(x[1])

        is_positive = difference > 0
        if is_positive:
            e_change = e_rise
            difference_formatted = f'++{difference:.1f}'
        else:
            e_change = e_fall
            difference_formatted = f'-{difference:.1f}'
        tmp = f'{product}: {e_money}{amount:.0f}({e_change}{difference_formatted})'
        formatted.append(tmp)


    return formatted

def format_dataframe(df, formatter, as_one=False):
    df = df.reset_index().values.tolist()
    df_formatted = formatter(df)
    if as_one:
        df_formatted = ['\n'.join(df_formatted)]
        
    return df_formatted

    
