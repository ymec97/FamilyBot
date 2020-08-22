#!/usr/bin/python3
import sys
from time import sleep
import logging
from telegram.ext import MessageHandler, Filters, CommandHandler, Updater

import Commands.CommandsLogic

# For debug purposes
import pdb

def get_token():
    """ Read bot token from file """
    return open("APIs/Telegram/CohenFamilyBot/token.txt").read()

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
    token = get_token()
    
    updater = Updater(token=get_token(), use_context=True)
    dispatcher = updater.dispatcher

    commandsExecutioner = Commands.CommandsLogic.Executioner()
    
    # Handlers
    startHandler = CommandHandler('start', commandsExecutioner.start)
    problemsHandler = CommandHandler('problems', commandsExecutioner.problems)
    reportHandler = CommandHandler('report', commandsExecutioner.report)
    solveHandler = CommandHandler('solve', commandsExecutioner.solve)
    solvedHandler = CommandHandler('solved', commandsExecutioner.solved)
    unknownHandler = MessageHandler(Filters.command, commandsExecutioner.unknown)
    

    dispatcher.add_handler(startHandler)
    dispatcher.add_handler(problemsHandler)
    dispatcher.add_handler(reportHandler)
    dispatcher.add_handler(solveHandler)
    dispatcher.add_handler(solvedHandler)

    # Unknown command handler must be added last - commands registerd after it won't be recognized as commands
    dispatcher.add_handler(unknownHandler)
    
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()  
    sys.exit(0)  
else:
    print("Not a library")
    sleep(1)
    sys.exit(1)
