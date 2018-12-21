""" Temporary solution for subscriptions. Should be run once a day or so """

import os, sys; sys.path.insert(0, '..')
import telebot
from modules.subscription_sender import send_subscriptions
import schedule, time

def do_send_subscriptions():
    bot = telebot.TeleBot("591953777:AAGjypU1tY0RDhWQzWvbeNw5DrYNCfYSFZw")
    send_subscriptions(bot)

schedule.every().day.at("09:14").do(do_send_subscriptions)

while True:
    schedule.run_pending()
    time.sleep(60)
