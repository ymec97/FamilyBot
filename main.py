#!/usr/bin/python3
import sys
from time import sleep
import logging
from telegram.ext import MessageHandler, Filters, CommandHandler, Updater

from datetime import date

# For debug purposes
import pdb


MAX_SUPPORTED_OPEN_PROBLEMS = 100
MAX_SUPPORTED_FIXED_ISSUES = 100
DATE_FORMAT = "%d/%m/%Y"

class Problem():
    def __init__(self, id, description):
        self.id = id
        self.is_active = True
        self.description = description
        self.date_opened = date.today().strftime(DATE_FORMAT)
        self.date_closed = None # None until closed
        self.date_fixed = None # None until fixed

    def _today(self):
        return date.today().strftime(DATE_FORMAT)

    def fix(self):
        self.date_fixed = self._today
        self.is_active = False

class Problems():
    problems = {}
    fixed_issues = {}


    def __init__(self):
        for id in range(MAX_SUPPORTED_OPEN_PROBLEMS):
            self.problems[id] = None

    def _getFreeId(self):
        # Supporting up to 100 problems
        for id in self.problems.keys():
            if not self.problems[id]:
                return id

    def new_problem(self, description):
        newId = self._getFreeId()
        self.problems[newId] = Problem(newId, description)
        return newId

    def fix_problem(self, id):
        self.problems[id].fix()
        self.fixed_issues[id] = self.problems[id]
        self.problems[id] = None

    def del_problem(self, id):
        if self.problems[id] == None:
            return False

        self.problems[id] = None
        return True


    def get_open_problems(self):
        """ Return a list of unresolved Problem instances. """
        openProblems = []
        
        for problem in self.problems.values():
            if problem:
                openProblems.append(problem)
        
        return openProblems
        

probs = Problems()

def get_token():
    """ Read bot token from file """
    return open("APIs/Telegram/CohenFamilyBot/token.txt").read()

# Command logics
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def problems(update, context):
    """ Handle /problems command in the bot """
    text = "ID  Description"
    problems = probs.get_open_problems()

    if len(problems) == 0:
        # no unresolved problems
        context.bot.send_message(chat_id=update.effective_chat.id, text="No problems.")
        return True
    
    for problem in problems:
            text = "{0}\n{1}:  {2}".format(text, problem.id, problem.description)
            
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def report(update, context):
    """ Handle /report command in the bot """
    #context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(problems))
    problemId = probs.new_problem(''.join(context.args))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Awesome, reported - {0}. Task ID is: {1}".format(probs.problems[problemId].description, problemId))

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="נו חלאס.")


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
    token=get_token()
    
    updater = Updater(token=get_token(), use_context=True)
    dispatcher = updater.dispatcher
    
    # Handlers
    start_handler = CommandHandler('start', start)
    problems_handler = CommandHandler('problems', problems)
    report_handler = CommandHandler('report', report)
    unknown_handler = MessageHandler(Filters.command, unknown)


    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(problems_handler)
    dispatcher.add_handler(report_handler)
    dispatcher.add_handler(unknown_handler)
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()    
else:
    print("Not a library")
    sleep(1)
    sys.exit(1)
