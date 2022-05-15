import os
import time

import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.util import extract_command
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
# from telegram.ext import (
#     Updater,
#     CommandHandler,
#     CallbackQueryHandler,
#     ConversationHandler,
#     CallbackContext,
# )

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


API_TOKEN = '5242485578:AAEhCP3627rHXu0uc3Orf_0tD50ww1ynKQ4'

from process_commands import load_sheet, get_prices_for_last_date, get_product_price_history
from process_commands import get_product_price_biggest_change_first_week, get_product_price_biggest_change_last_week

# from data import load_sheet, get_prices_for_last_date, get_product_price_history
PRICES_DF, PRODUCTS, PRODUCT_CHOICE = load_sheet()
COMMANDS = ['start', 'product', 'prices_today', 'week_change']#, 'all_time_change'] #'budget']
VISUALIZE = False

bot = telebot.TeleBot(API_TOKEN)


def prepare_message_for_product_handler(message):
    message = message.text.strip()
    message = message.encode('utf-8').decode('utf-8')
    return message

def send_list_of_messages(message, message_list):
    for text in message_list:
        bot.send_message(message.chat.id, text)


def present_command_options(message, command=None):
	if command is None: 
		command = extract_command(message.text)
		if command not in COMMANDS:
			command = None

	bot.send_message(message.chat.id, "Хочешь узнать что нибудь еще?", 
		reply_markup=get_commands_keyboard(current_command=command))


def get_commands_keyboard(current_command=None):
	if current_command is not None and type(current_command) is str:
		commands = [cmd for cmd in COMMANDS if cmd != current_command]
	else:
		commands = COMMANDS.copy()

	markup = types.ReplyKeyboardMarkup(row_width=1)#len(commands))
	markup.add(*[types.KeyboardButton(f'/{cmd}') for cmd in commands])

	return markup

def remove_keyboard():
	markup = types.ReplyKeyboardRemove(selective=False)

	return markup

def get_products_keyboard():
    reply_keyboard, tofill_keyboard = [], []
    markup = types.ReplyKeyboardMarkup(row_width=3)
    for i, product in PRODUCT_CHOICE.items():
        tofill_keyboard.append(types.KeyboardButton(str(product)))
        if i % 3 == 0:
            markup.add(*tofill_keyboard)
            tofill_keyboard = []
    if len(tofill_keyboard) > 0:
        markup.add(*tofill_keyboard)

    return markup


@bot.message_handler(func=lambda message: prepare_message_for_product_handler(message) in PRODUCTS)
def price_product_selected(message):
    """Sends a message with three inline buttons attached."""
    logger.info(message.text)
    i = PRODUCTS.index(message.text)

    bot.reply_to(message, f"{message.text} стоит:", reply_markup=remove_keyboard())
    product_price_history = get_product_price_history(PRICES_DF, PRODUCT_CHOICE, i)
    send_list_of_messages(message, product_price_history)
    if VISUALIZE:
        bot.send_message(message.chat.id, "И вдогонку визуализация:")
        prices_change_img = open(f'{i}.png', 'rb')
        bot.send_photo(message.chat.id, prices_change_img)
    present_command_options(message)


@bot.message_handler(commands=['prices_today'])
def price_today(message):
    """Sends a message with three inline buttons attached."""
    bot.reply_to(message, f'Давай узнаем как менялись цены:', reply_markup=remove_keyboard())
    prices_today = get_prices_for_last_date(PRICES_DF)
    send_list_of_messages(message, prices_today)
    present_command_options(message)


@bot.message_handler(commands=['product'])
def price_product(message):
    """Sends a message with three inline buttons attached."""
    bot.reply_to(message, "Давай узнаем какие цены на продукты на сегодня", reply_markup=remove_keyboard())
    bot.send_message(message.chat.id, "Выбери продукт из списка ниже:",reply_markup=get_products_keyboard())

@bot.message_handler(commands=['week_change'])
def price_week_change(message):
    """Sends a message with three inline buttons attached."""
    bot.reply_to(message, "Эти продукты менялись в цене больше всего за последнюю неделю:", reply_markup=remove_keyboard())
    prices_week_change = get_product_price_biggest_change_last_week(PRICES_DF)
    send_list_of_messages(message, prices_week_change)
    present_command_options(message)

@bot.message_handler(commands=['all_time_change'])
def price_all_time_change(message):
    """Sends a message with three inline buttons attached."""
    bot.reply_to(message, "Эти продукты менялись в цене больше всего с первой недели:", reply_markup=remove_keyboard())
    prices_all_change = get_product_price_biggest_change_first_week(PRICES_DF)
    send_list_of_messages(message, prices_all_change)
    present_command_options(message)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {bot.get_chat(message.chat.id).first_name}. Я помогу тебе узнать как менялись цены на продукты и распланировать бюджет!')

    time.sleep(1)
    
    bot.send_message(message.chat.id, 'Чтобы увидеть, какие продукты больше всего поменялись в цене за последнюю неделю, выбери /week_change.')
    time.sleep(0.5)
    # bot.send_message(message.chat.id, 'Или за последнюю неделю. Для этого выбери /all_time_change.', reply_markup=get_commands_keyboard(extract_command(message.text)))

    time.sleep(1)
    # bot.send_message(message.chat.id, 'Но это не все! Я могу помочь тебе в других вопросах тоже.')

    bot.send_message(message.chat.id, 'Если хочешь узнать цены на продукты на сегодня, выбери /today.')
    time.sleep(0.2)
    bot.send_message(message.chat.id, 'Если хочешь узнать как менялись цены на определенный продукт, выбери /product.')
    time.sleep(0.2)

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    logger.info(message.text)
    bot.send_message(message.chat.id, "Напиши /start чтобы начать")

bot.infinity_polling()
