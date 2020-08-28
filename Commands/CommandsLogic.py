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

class Executioner():

	def __init__(self):
		self.problemsLog = Problems.ProblemsLog.Manager()
		self._unknownCounter = 0 # Used to iterate "unknown command" responses

	# Command logics
	def start(self, update, context):
	    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

	def problems(self, update, context):
	    """ Handle /problems command in the bot """
	    text = ""
	    problems = self.problemsLog.get_open_problems()

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

	def report(self, update, context):
	    """ 
	    Handle /report command in the bot 

	    usage: /report [description]
	    """
	    usageMessage = "usage: /report [description]"
	    text = "Nothing to report. Please describe the problem\n" + usageMessage
	    if len(context.args) != 0:
	        # Problem description passed with the command
	        problemId = self.problemsLog.new_problem(' '.join(context.args))
	        text="Awesome, reported - {0}. Task ID is: {1}".format(self.problemsLog.problems[problemId].description, problemId)

	    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

	def solve(self, update, context):
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
	    if self.problemsLog.fix_problem(problemId):
	        text="Awesome\nproblem with ID {0} solved!".format(problemId)

	    else:
	        text="Sorry, problem with ID: {0} doesn't exist".format(problemId)

	    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

	    return True

	def solved(self, update, context):
	    """ 
	    Handle /solved command in the bot 

	    usage: /solved

	    :returns False when invalid parameters are supplied. True if a the solved problems list was printed successfuly
	    """
	    SOLVED_PARAM_COUNT = 0
	    usageMessage = "usage: /solved"
	    solvedProblems = self.problemsLog.get_solved_problems()
	    # problems descriptions are appended here later
	    text = ""

	    if len(context.args) != SOLVED_PARAM_COUNT:
	        if len(context.args) > SOLVED_PARAM_COUNT:
	            text = "Please don't add anyting to the command\n" + usageMessage
	        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

	        return False
	    
	    if len(solvedProblems) == 0:
	        text = "No solved problems to show"
	        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

	        return True

	    for problem in solvedProblems:
	        solveDate = problem.get_date_solved()
	        if solveDate != date.today():
	            text = "{0}\nID {1}: {2} [closed on {3}]".format(text, problem.id, problem.description, solveDate)
	        else:
	            text = "{0}\nID {1}: {2} [closed today]".format(text, problem.id, problem.description, solveDate)
	    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

	    return True


	def unknown(self, update, context):
	    responses = ["הפקודה לא נתמכת.", "די.", "נו חלאס!"]
	    
	    # Calculate response using counter, make sure counter never gets out of scope
	    response = responses[self._unknownCounter % len(responses)]
	    self._unknownCounter = (self._unknownCounter + 1) % len(responses)    

	    context.bot.send_message(chat_id=update.effective_chat.id, text=response)

	    return True