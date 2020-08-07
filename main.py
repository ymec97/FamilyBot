#!/usr/bin/python3
import sys
from time import sleep
from telegram.ext import Updater
import logging
from telegram.ext import MessageHandler, Filters, CommandHandler


# For debug purposes
import pdb


problems = ["שטויות", "בלאגן"]

def getToken():
	""" Read bot token from file """
	return open("APIs/Telegram/CohenFamilyBot/token.txt").read()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def status(update, context):
	""" Handle /status command in the bot """
	context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(problems))

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="נו חלאס.")

def main():
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
	token=getToken()
	
	updater = Updater(token=getToken(), use_context=True)
	dispatcher = updater.dispatcher
	
	# Handlers
	start_handler = CommandHandler('start', start)
	status_handler = CommandHandler('status', status)
	unknown_handler = MessageHandler(Filters.command, unknown)


	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(status_handler)
	dispatcher.add_handler(unknown_handler)
	
	updater.start_polling()
	

if __name__ == '__main__':
    main()    
else:
    print("Not a library")
    sleep(1)
    sys.exit(1)
