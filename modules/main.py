import os, sys; sys.path.insert(0, '..')
import telebot

from constants.global_constants import *
from modules.parse_message import parse_message
from modules.processing_module import process_request_objects
from modules.actions_generator import generate_actions
from modules.performer import do_actions
from modules.utilities import write_chat_id
from time import sleep


# There exists some internal error in this API, so we need to
# wrap it in while True: try-catch. (It can throw an error, but not too often (may be once a day))
while True:
    try:
        bot = telebot.TeleBot("591953777:AAGjypU1tY0RDhWQzWvbeNw5DrYNCfYSFZw")  # type = telebot.Telebot


        @bot.message_handler(commands=['start'])
        def send_welcome(message):
            """ Greeting function. Also sends help message """
            message_filename = os.path.join(MESSAGES_PATH, 'start.txt')
            with open(message_filename, 'r') as f:
                start_message = f.read()
            bot.send_message(message.chat.id, start_message)


        @bot.message_handler(commands=['help'])
        def send_help(message):
            """ Prints help message, that explains, how to use this program. """
            message_filename = os.path.join(MESSAGES_PATH, 'help.txt')
            with open(message_filename, 'r') as f:
                help_message = f.read()
            bot.send_message(message.chat.id, help_message)


        @bot.message_handler(func=lambda m: True)
        def echo_all(message):
            """This function connects main logic to TeleBot API and reacts to all the incoming messages."""
            message_text = str(message.text)
            user_id = str(message.from_user.id)
            chat_id = str(message.chat.id)

            # bot.send_message(message.chat.id, 'I am alive :)')

            request_objects = parse_message(message_text, user_id)
            response_objects = process_request_objects(request_objects, user_id)
            actions = generate_actions(response_objects)
            do_actions(actions=actions, bot=bot, chat_id=chat_id)
            write_chat_id(user_id=user_id, chat_id=chat_id)

        bot.polling(none_stop=True, timeout=60)
    except Exception:
        bot.stop_polling()
        sleep(2)


# Old block
# try:
#     for entry in react_to_message(message.text):
#         task = entry[0]
#         args = entry[1:]
#         if task == 'sendErrorMessage':
#             bot.send_message(message.chat.id, args, parse_mode='HTML')
#             raise Exception
#         if task == 'sendMessage':
#             bot.send_message(message.chat.id, args, parse_mode='HTML')
#         if task == 'sendPlot':
#             bot.send_photo(message.chat.id, open(args[0], 'rb'), args[1], parse_mode='HTML')
#             os.remove(args[0])
#         if task == 'sendPhoto':
#             bot.send_photo(message.chat.id, open(args[0], 'rb'), args[1], parse_mode='HTML')
#             os.remove(args[0])
#     with open('log.txt', 'a') as log:
#         log.write(f'OK - {message.text}\n')
# except Exception as e:
#     with open('log.txt', 'a') as log:
#         log.write(f'FAILED - {message.text}\n')
