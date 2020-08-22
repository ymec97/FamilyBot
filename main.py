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
    token=get_token()
    
    updater = Updater(token=get_token(), use_context=True)
    dispatcher = updater.dispatcher
    
    # Handlers
    start_handler = CommandHandler('start', Commands.CommandsLogic.start)
    problems_handler = CommandHandler('problems', Commands.CommandsLogic.problems)
    report_handler = CommandHandler('report', Commands.CommandsLogic.report)
    solve_handler = CommandHandler('solve', Commands.CommandsLogic.solve)
    solved_handler = CommandHandler('solved', Commands.CommandsLogic.solved)
    unknown_handler = MessageHandler(Filters.command, Commands.CommandsLogic.unknown)
    

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(problems_handler)
    dispatcher.add_handler(report_handler)
    dispatcher.add_handler(solve_handler)
    dispatcher.add_handler(solved_handler)

    # Unknown command handler must be added last - commands registerd after it won't be recognized as commands
    dispatcher.add_handler(unknown_handler)
    
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()    
else:
    print("Not a library")
    sleep(1)
    sys.exit(1)
