#!/usr/bin/python3
import sys
from time import sleep
import logging
from telegram.ext import MessageHandler, Filters, CommandHandler, Updater

from datetime import date

# For debug purposes
import pdb

"""
Commands list (in botfather format):

start    - Start a new conversation with the bot
problems - View open problems reported in the past
report   - Open a new problem to be solved
solve    - Mark a problem as solved
solved    - View solved problems
"""

MAX_SUPPORTED_OPEN_PROBLEMS = 100
MAX_SUPPORTED_FIXED_ISSUES = 100
DATE_FORMAT = "%d/%m/%Y"

class Problem():
    def __init__(self, id, description):
        self.id = id
        self.isActive = True
        self.description = description
        self.dateOpened = date.today()
        self.dateClosed = None # None until closed
        self.dateSolved = None # None until solved

    def fix(self):
        self.dateSolved = date.today()
        self.isActive = False

    def days_open(self):
        """ return int indicating how many days the issue is open """
        latestActiveDate = date.today() # Meaning still unresolved
        if self.dateClosed:
            latestActiveDate = self.dateClosed
        elif self.dateSolved:
            latestActiveDate = self.dateSolved

        return (latestActiveDate - self.dateOpened).days

    def get_date_opened(self):
        """ Return a string representing the date the problem was opened in"""
        return self.dateOpened.strftime(DATE_FORMAT)
    def get_date_solved(self):
        """ Return a string representing the date the problem was solved in"""
        return self.dateSolved.strftime(DATE_FORMAT)
    
    def get_date_closed(self):
        """ Return a string representing the date the problem was closed in"""
        return self.dateClosed.strftime(DATE_FORMAT)

class Problems():
    # a dictionary of ID: Problem
    problems = {}

    # a dictionary of ID: [Problem0, Problem1..] - closed/solved problems free their ID and duplicates can occur for closed/solved
    solvedProblems = {}


    def __init__(self):
        for id in range(MAX_SUPPORTED_OPEN_PROBLEMS):
            self.problems[id] = None
            self.solvedProblems[id] = None

    def _getFreeId(self):
        # Supporting up to 100 problems
        for id in self.problems.keys():
            if not self.problems[id]:
                return id

    def _getUsedIds(self):
        usedIds = []
        for id in self.problems.keys():
            if self.problems[id]:
                usedIds.append(id)

        return usedIds

    def new_problem(self, description):
        newId = self._getFreeId()
        self.problems[newId] = Problem(newId, description)
        return newId

    def fix_problem(self, id):
        """ 
        Mark a problem as closed and free id 

        :param id The id to mark as solved
        :type     int
        :returns  False when id doesn't exist. True otherwise
        """
        if id not in self._getUsedIds():
            return False

        # First time an issue with this ID is solved
        if not self.solvedProblems[id]:
            self.solvedProblems[id] = []

        self.problems[id].fix()
        self.solvedProblems[id].append(self.problems[id])
        self.problems[id] = None

        return True

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
        
    def get_fixed_problems(self):
        """ Return a list of solved Problem instances. """
        solvedProblems = []
        
        for problem in self.solvedProblems.values():
            if problem:
                # self.solvedProblems values has a list of problems as values
                solvedProblems.extend(problem)

        return solvedProblems

probs = Problems()

def get_token():
    """ Read bot token from file """
    return open("APIs/Telegram/CohenFamilyBot/token.txt").read()

# Command logics
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def problems(update, context):
    """ Handle /problems command in the bot """
    text = ""
    problems = probs.get_open_problems()

    if len(problems) == 0:
        # no unresolved problems
        context.bot.send_message(chat_id=update.effective_chat.id, text="No problems.")
        return True
    
    for problem in problems:
        openDuration = problem.days_open()
        if openDuration > 0:
            text = "{0}\nID {1}: {2} [{3}d open".format(text, problem.id, problem.description, openDuration)
        else:
            text = "{0}\nID {1}: {2} [opened today]".format(text, problem.id, problem.description, openDuration)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def report(update, context):
    """ 
    Handle /report command in the bot 

    usage: /report [description]
    """
    usageMessage = "usage: /report [description]"
    text = "Nothing to report. Please describe the problem\n" + usageMessage
    if len(context.args) != 0:
        # Problem description passed with the command
        problemId = probs.new_problem(' '.join(context.args))
        text="Awesome, reported - {0}. Task ID is: {1}".format(probs.problems[problemId].description, problemId)

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def solve(update, context):
    """ 
    Handle /solve command in the bot 

    usage: /solve [ID]

    :returns False when invalid parameters are supplied. True if a problem was marked as solved.
    """
    SOLVE_PARAM_COUNT = 1
    usageMessage = "usage: /solve [ID]"

    if len(context.args) != SOLVE_PARAM_COUNT:
        if len(context.args) == 0:
            text = "Nothing to solve. Please add the problem ID\n" + usageMessage
        else:
            text = "Too many parameters to command\n" + usageMessage
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

        return False
    
    problemId = context.args[0]
    if not problemId.isnumeric():
        text = "Invalid problem ID supplied.\n" + usageMessage
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

        return False
    
    problemId = int(problemId)
    if probs.fix_problem(problemId):
        text="Awesome\nproblem with ID {0} solved!".format(problemId)

    else:
        text="Sorry, problem with ID: {0} doesn't exist".format(problemId)

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return True

def solved(update, context):
    """ 
    Handle /solved command in the bot 

    usage: /solved

    :returns False when invalid parameters are supplied. True if a the solved problems list was printed successfuly
    """
    FIXED_PARAM_COUNT = 0
    usageMessage = "usage: /solved"
    solvedProblems = probs.get_fixed_problems()
    # problems descriptions are appended here later
    text = ""

    if len(context.args) != FIXED_PARAM_COUNT:
        if len(context.args) > FIXED_PARAM_COUNT:
            text = "Please don't add anyting to the command\n" + usageMessage
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

        return False
    
    if len(solvedProblems) == 0:
        text = "No solved problems to show"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

        return True

    for problem in solvedProblems:
        fixDate = problem.get_date_solved()
        if fixDate != date.today():
            text = "{0}\nID {1}: {2} [closed on {3}]".format(text, problem.id, problem.description, fixDate)
        else:
            text = "{0}\nID {1}: {2} [closed today]".format(text, problem.id, problem.description, fixDate)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return True


def unknown(update, context):
    responses = ["הפקודה לא נתמכת.", "די.", "נו חלאס!"]
    if not hasattr(unknown, "counter"):
        unknown.counter = 0
    
    # Calculate response using counter, make sure counter never gets out of scope
    response = responses[unknown.counter % len(responses)]
    unknown.counter = (unknown.counter + 1) % len(responses)    

    context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    return True



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
    solve_handler = CommandHandler('solve', solve)
    solved_handler = CommandHandler('solved', solved)
    unknown_handler = MessageHandler(Filters.command, unknown)
    

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
