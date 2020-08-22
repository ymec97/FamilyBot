from datetime import date
import Problems.ProblemsLog


"""
Commands list (in botfather format):

start    - Start a new conversation with the bot
problems - View open problems reported in the past
report   - Open a new problem to be solved
solve    - Mark a problem as solved
solved    - View solved problems
"""

probs = Problems.ProblemsLog.Manager()

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