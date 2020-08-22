from datetime import date
import Shared.Standards

class Problem():
    """
    Binding operations needed to manage a problem
    """
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
        return self.dateOpened.strftime(Shared.Standards.DATE_FORMAT)
    def get_date_solved(self):
        """ Return a string representing the date the problem was solved in"""
        return self.dateSolved.strftime(Shared.Standards.DATE_FORMAT)
    
    def get_date_closed(self):
        """ Return a string representing the date the problem was closed in"""
        return self.dateClosed.strftime(Shared.Standards.DATE_FORMAT)

class Manager():
    """
    Managing open and solved problems
    """
    MAX_SUPPORTED_OPEN_PROBLEMS = 100
    MAX_SUPPORTED_SOLVED_ISSUES = 100

    # a dictionary of ID: Problem
    problems = {}

    # a dictionary of ID: [Problem0, Problem1..] - closed/solved problems free their ID and duplicates can occur for closed/solved
    solvedProblems = {}


    def __init__(self):
        for id in range(self.MAX_SUPPORTED_OPEN_PROBLEMS):
            self.problems[id] = None

        for id in range(self.MAX_SUPPORTED_SOLVED_ISSUES):
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
        
    def get_solved_problems(self):
        """ Return a list of solved Problem instances. """
        solvedProblems = []
        
        for problem in self.solvedProblems.values():
            if problem:
                # self.solvedProblems values has a list of problems as values
                solvedProblems.extend(problem)

        return solvedProblems