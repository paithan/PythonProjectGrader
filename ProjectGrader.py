"""A project grader for programming projects written in Python 3.x.  
   Author: Kyle W. Burke (kwburke@plymouth.edu) """


##### Issues List
# TODO: Docstring tests still print out 0/0 when they succeed.  Need to get rid of that.  I don't want it to say anything.


import traceback
import time
import math
import copy
import sys
import re
#sys.path.append('../../swampy.1.1/')
#from TurtleWorld import *
import io # https://docs.python.org/3/library/io.html#io.StringIO
import types
import importlib
from pathlib import Path
import stat

def get_whitespace_prefix(string):
    """Returns the longest prefix of a given string composed only of tabs and spaces."""
    index = 0
    prefix = ""
    while index < len(string) and string[index] in "\t ":
        prefix += string[index]
        index += 1
    return prefix

def get_function_text(function):
    """Returns a user-defined function's code as a string."""
    import linecache
    line_number = function.__code__.co_firstlineno + 1#get the first line after the header
    file_name = function.__code__.co_filename
    current_line = linecache.getline(file_name, line_number)
    indentation = get_whitespace_prefix(current_line)
    #skip past any empty lines at the beginning of the function
    while(indentation == "" and current_line == "\n"):
        #the first line(s) has no indentation and no code.  Move to the next line.
        #world = TurtleWorld()
        line_number += 1
        current_line = linecache.getline(file_name, line_number)
        indentation = get_whitespace_prefix(current_line)
    #print("indentation: '" + indentation + "'")
    #print(current_line)
    function_text = ""
    while current_line.startswith(indentation) or current_line.strip() == "":
        function_text += current_line
        line_number += 1
        current_line = linecache.getline(file_name, line_number)
            
    return function_text
    
def is_recursive(function):
    """Returns whether a function is directly recursive.  (Use has_recursive_helper to test whether a function is a wrapper.)"""
    if (function.__name__ in get_function_text(function)):
        return True
    return False

def has_recursive_helper(function):
    """Returns whether a function has a recursive helper function (that must be user-defined).  Warning: it's not very complete.  Doesn't do methods or import packages."""
    helpers = get_functions(function)
    for helper in helpers:
        if is_recursive(helper):
            return True
    return False

def get_functions(function):
    """Returns a list of the functions called by the argument function."""
    body = get_function_text(function)
    functions = []
    in_possible_function = False
    in_spaces = False
    current_function_string = ""
    function_characters = "abcdefghijklmnopqrstuvwxyz1234567890_."
    spaces = " \t"
    for char in body:
        if char.lower() in function_characters:
            if in_spaces:
                #this is a new function
                in_spaces = False
                current_function_string = "" + char
            else:    
                #in_spaces is already False
                current_function_string += char
            in_possible_function = True
        elif char in spaces:
            #a space!  If the next non-space thing we see is an open paren, this will be a function call.
            in_spaces = True
        else:
            if char == '(':
                if in_possible_function:
                    try:
                        called_function = eval(current_function_string)
                        if (type(called_function) != type(get_functions)):
                            pass
                            #print(called_function.__name__ + " is not user-defined!")
                        else:
                            functions.append(called_function)
                    except:
                        pass
                        #print("I can't eval the function " + current_function_string)
            in_possible_function = False
            current_function_string = ""
            in_spaces = False
    return functions

def prettyPrint(thing):
    """Returns a pretty string version of thing independent of whether it is primitive, an object, or a list or tuple."""
    #TODO: include a case for a function?
    #How do you do this?!?!?
    if isinstance(thing, list):
        string = "["
        for i in range(len(thing)):
            string += prettyPrint(thing[i])
            if i < len(thing) - 1:
                string += ", "
        string += "]"
        return string
    elif isinstance(thing, tuple):
        string = "("
        for i in range(len(thing)):
            string += prettyPrint(thing[i])
            if i < len(thing) - 1:
                string += ", "
        string += ")"
        return string
    elif isinstance(thing, object):
        #return thing.__str__()
        #TODO: can we do this instead?
        return str(thing)
    else:
        return str(thing)
        
     
class FunctionTest(object):
    """A test for a function to see whether it is working as expected.
    attributes: description, subFunctions, parameters, correctnessTest, passMessage, passPoints, failMessage, failPoints, results."""
    
    def __init__(self, description, isCalled, parameters, correctnessTest, passMessage, passPoints, passSubtests, failMessage, failPoints, failSubtests, preRunStatements = [], postRunStatements = []):
        self.description = description
        self.isCalled = isCalled
        self.parameters = parameters
        self.correctnessTest = correctnessTest
        self.passMessage = passMessage
        self.passPoints = passPoints
        self.passSubtests = passSubtests
        self.failMessage = failMessage
        self.failPoints = failPoints
        self.failSubtests = failSubtests
        self.preRunStatements = preRunStatements
        self.postRunStatements = postRunStatements
        self.prepass_expressions = []
        #self.postRunStatements.append("print(printedOutput)")
        #self.postRunStatements.append("print(printedOutput == \"No, 134 isn't divisible
        
    def __str__(self):
        return "A Function Test.  Description: " + self.description + "\n Tests function with parameters: " + prettyPrint(self.parameters) + "\n Uses this test (string) for correctness: " + prettyPrint(self.correctnessTest) + "\n This test has value: " + prettyPrint(self.passPoints) + "."
        
    def add_prepass_expression_as_string(self, string):
        self.prepass_expressions.append(string)
        
    def getParameters(self): #do we need to add a package name?
        """Returns the parameters of this."""
        try:
            return copy.deepcopy(self.parameters)
        except:
            return self.parameters
        
    def isPositiveTest(self):
        """Returns whether this test is looking for correctness.  The alternative is looking for incorrectness."""
        return passPoints > 0
        
    def runTestOnFunction(self, functionName, module=None, className=None):
        """Returns a FunctionResults object describing the result of the function run on the tests."""
        #first, build the string corresponding to the whole function name, including class and module
        if className == None or className == "":
            functionString = functionName
        else:
            functionString = className + "." + functionName
        if module != None:
            functionString = "module." + functionString
        
        #print("functionString: " + functionString)
        #let's get on with the testing!
        part_results = FunctionResults() #we'll add to this the results of testing
        
        #reload the module to destroy attempts at using global variables
        module = importlib.reload(module)
        
        passed = False  #False until we pass the test
        
        #There might be some reasons to pass this before we even try the tests.  (For example, this may require user input and we've already passed it in a previous round.)
        for expression in self.prepass_expressions:
            passed = passed or eval(expression)
        prepass = passed #if we've already passed, then we've prepassed
        if not passed:
        
            #new version?
            pre_run = ""
            for statement in self.preRunStatements:
                pre_run += statement + "\n"
            try:
                pre_code = compile(pre_run, 'pre_run_stuff', 'exec')
                exec(pre_code) 
            except Exception as err:
                print("Failed while exec-ing some pre-run statements.  Code:\n", pre_run)   
                print("Problem:", err, "\n")
            
            #Set up variables for the test by executing any necessary pre-test statements.
#             for statement in self.preRunStatements:
#                 try:
#                     exec(statement)
#                 except:
#                     print("Execing preRunStatement failed:", statement)
#                     print("(Perhaps a class name has been misspelled?)")
#                     print("Function: " + functionName + "   statement: " + statement)
#                     exec(statement) #still cause the error!
            
            #Evaluate any parameters
            parameters = []
            for statement in self.parameters:
                parameters.append(eval(str(statement)))
                #I decided it was a bad idea to let this fly.  If the parameter can't be evaluated, treating it as a string is dangerous
                #try:
                #    parameters.append(eval(str(statement)))
                #except:
                #    #sometimes the parameter is just the value itself; it shouldn't be evaluated further.
                #    parameters.append(statement)
                
            #Redirect sys.stdout so we don't have to print everything
            oldStdout = sys.stdout #save the old stdout value
            result = io.StringIO() #get a new variable to store everything that would go to standard output
            sys.stdout = result #set our new variable to catch the printed output
            didNotRun = False
            try:
                #print('Evaling functionString:',functionString)
                #print(module)
                #print(module.print_checker_space_row)
                givenFunction = eval(functionString)
                if (self.isCalled):
                    output = givenFunction(*(parameters))
                    sys.stdout = oldStdout  #reset the old stdout
                    printedOutput = result.getvalue()
                    printedOutput = printedOutput[0:-1]
                    if printedOutput.strip() != "":
                        pass
                        #print('printedOutput between star-pairs:\n**' + printedOutput + '**')
                        #print('len(printedOutput):', len(printedOutput))
                    #print 'output=', output
                #print('Testing:', self.correctnessTest)
                try:
                    #debugging.  Delete this block later
                    #print("About to run the test: " + str(self.correctnessTest)) 
                    #try :
                    #    print("'" + eval("printedOutput.strip()") + "'")
                    #    print(eval("printedOutput.strip() == '| | | | | | | | |'"))
                    #except:
                    #    pass
                    
                    passed = eval(self.correctnessTest) #ACTUALLY RUN THE TEST!
                except:
                    #if the test crashes, then the code fails.  TODO: talk about how this failed and add a message in the grade?
                    passed = False
            except:
                #test crashed while trying to evaluate the function string and the parameters.  Something really weird must be happening in the code we're testing
                passed = False
                didNotRun = True
                sys.stdout = oldStdout #in case it didn't get reset before
                traceback.print_exc()
                printedOutput = result.getvalue()
                if printedOutput.strip() != "":
                    print(printedOutput)
            sys.stdout = oldStdout #in case it didn't get reset before
            
        #execute any post-test statements to clean things up
        if not prepass:
            for statement in self.postRunStatements:
                exec(statement)
                
        if passed:
            #The test passed!  Add the correct messages, etc!
            #print('Passed test:', self.passMessage)
            passedSubtest = False
            for subtest in self.passSubtests:
                subtestResults = subtest.runTestOnFunction(functionName, module, className)  #subtestResults is a PartResults object
                #if we pass any of the subtests, then we're okay
                passedSubtest = passedSubtest or (not (subtestResults.everything_incorrect()))
                #for subtestResult in subtestResults:
                #    passedSubtest = passedSubtest or subtestResult.passed()
                part_results.add_result(subtestResults)
            if not passedSubtest:
                #didn't pass any subtests, so we need to tell the user we did pass this test.  Otherwise, this test result is eclipsed by the subtests
                part_results.add_new_result(self.passMessage, self.passPoints, self.passPoints)
        else: 
            #did not pass this test
            print('Failed test for ', functionName + ": " + self.failMessage)
            failedSubtest = False
            for subtest in self.failSubtests:
                subtestResults = subtest.runTestOnFunction(functionName, module, className)
                for subtestResult in subtestResults:
                    failedSubtest = failedSubtest or (not subtestResult.passed())
                part_results.add_result(subtestResults)
            if not failedSubtest:
                #didn't fail any subtests, so we need to tell the user we did fail this test.  Otherwise, this test result is eclipsed by the subtests
                if didNotRun and self.isCalled:
                	#the function was run and it caused an exception.
                	    function_or_method = "function"
                	    if className != None:
                	        function_or_method = "method"
                	    message = "This " + function_or_method + " either causes exceptions or does not finish running."
                	    points = 0
                	    part_results.add_new_result(message, points, self.passPoints)
                else:
                    part_results.add_new_result(self.failMessage, self.failPoints, self.passPoints)
            #if this fails, print out why
            if not part_results.full_credit():
                print("~~~~~~~~~~~~~`Found an error!!!!!~~~~~~~~~~~~~~\n", str(part_results))
        return part_results
        
        
class AtomicFunctionTest(FunctionTest):
    """A single test.
    attributes: parameters - the list of parameters that the function will be called on; correctnessTest - string version of test to be invoked to see whether the function worked; messages: [passMessage, failMessage]; points: [passPoints, failPoints]."""
    
    def __init__(self, parameters, correctnessTest, messages, points, description = "Atomic test for a function.", preRunStatements = [], postRunStatements = []):
        FunctionTest.__init__(self, description, True, parameters, correctnessTest, messages[0], points[0], [], messages[1], points[1], [], preRunStatements, postRunStatements)
        
        
class FruitfulManyTryTest(AtomicFunctionTest):
    '''Tries the function many times, where just one needs to return the correct value.'''
    
    def __init__(self, parameters, target_value, num_tries, messages, points, pre_run_statements = [], post_run_statements = []):
        pre_run_statements = pre_run_statements + ["returned_values = []", "function_to_test = eval(functionString)", 'params = []', 'for param_statement in self.parameters:\n    params.append(eval(str(param_statement)))', 'for i in range(' + str(num_tries) + '):\n    return_val = function_to_test(*(params))\n    returned_values.append(return_val)']
        correctness_test = str(target_value) + " in returned_values"
        FunctionTest.__init__(self, "Tests to see whether the function ever returns a value.", True, parameters, correctness_test, messages[0], points[0], [], messages[1], points[1], [], pre_run_statements, post_run_statements)
        
        
class LenientPrintingFunctionTest(AtomicFunctionTest):
    """An atomic test for functions that are void but print output that allows for a few different options.  Be sure to put \\n in the goalStrings for any line breaks as it needs to escape twice!"""
    
    def __init__(self, parameters, goal_strings, messages, points, preRunStatements = [], postRunStatements = []):
        fixed_goal_strings = []
        to_strip = True #if this becomes False, we won't add a ".strip()" after the printedOutput
        for goal_string in goal_strings:
            fixed_goal_string = goal_string.replace("'", "\\'")
            if (goal_string.strip() != goal_string):
                to_strip = False
            fixed_goal_strings.append(fixed_goal_string)
        correctness_test = "printedOutput"
        if to_strip:
            correctness_test += ".strip()"
        correctness_test += " in " + str(fixed_goal_strings)
        #print("correctness_test: " + correctness_test)
        AtomicFunctionTest.__init__(self, parameters, correctness_test, messages, points, "Checks whether the output of a function matches one of these: " + str(goal_strings), preRunStatements, postRunStatements)
             
                        
class PrintingFunctionTest(AtomicFunctionTest):
    """An atomic test for functions that are void, but print output.
    Be sure to put \\n in the goalString for any line breaks, as it needs to escape twice!"""
    
    def __init__(self, parameters, goalString, messages, points, preRunStatements = [], postRunStatements = []):
        correctnessTest = "printedOutput"
        #goalString = goalString.replace("\\", "\\\\") This didn't work.
        #print("new goalString:", goalString)
        goalString = goalString.replace("'", "\\'")
        if (goalString.strip() == goalString):
            correctnessTest += ".strip()"
        correctnessTest += " == '" + goalString + "'"
        AtomicFunctionTest.__init__(self, parameters, correctnessTest, messages, points, "Checks whether the output of a function matches " + goalString + ".", preRunStatements, postRunStatements)
        
class PrintingIncludesStringFunctionTest(AtomicFunctionTest):
    """Test to see whether a string is in the printed output."""
    
    def __init__(self, parameters, goal_string, messages, points, preRunStatements = [], postRunStatements = []):
        correctnessTest = "printedOutput"
        #goalString = goalString.replace("\\", "\\\\") This didn't work.
        #print("new goalString:", goalString)
        goal_string = goal_string.replace("'", "\\'")
        if (goal_string.strip() == goal_string):
            correctnessTest += ".strip()"
        correctnessTest = "'" + goal_string + "' in " + correctnessTest
        AtomicFunctionTest.__init__(self, parameters, correctnessTest, messages, points, "Checks whether the output of a function includes " + goal_string + ".", preRunStatements, postRunStatements)
        
        
class PrintingRegularExpressionTest(AtomicFunctionTest):
    """An Atomic test for functions that print to the screen with many acceptable results.  Accepts any output that matches a given regular expression."""
    
    def __init__(self, parameters, reg_ex, messages, points, pre_run_statements = [], post_run_statements = []):
        printedOutputString = 'printedOutput'
        if reg_ex.strip() == reg_ex:
            #Let's strip off the students' extra whitespace, just in case.
            printedOutputString = printedOutputString + '.strip()'
        correctness_test = "re.compile(\"" + reg_ex + "\").fullmatch(" + printedOutputString + ") != None"
        AtomicFunctionTest.__init__(self, parameters, correctness_test, messages, points, "Checks whether the printed output matches regular expression " + reg_ex + ".", pre_run_statements, post_run_statements)
        
        
class FruitfulFunctionTest(AtomicFunctionTest):
    """An Atomic test for functions that return a value.  Passes when the output is exactly the specified goalValue; fails otherwise.  goalValue must be given as a string, unfortunately."""
    
    def __init__(self, parameters, goalValue, messages, points, preRunStatements = [], postRunStatements = []):
        correctnessTest = "output == " + str(goalValue)
        AtomicFunctionTest.__init__(self, parameters, correctnessTest, messages, points, "Checks whether the return value of a function equals " + str(goalValue) + ".", preRunStatements, postRunStatements) 


class FruitfulRegularExpressionTest(AtomicFunctionTest):
    """An atomic test functions that return a string where the result can be anything matching a regular expression."""
    def __init__(self, parameters, reg_ex, messages, points, pre_run_statements = [], post_run_statements = []):
        correctness_test = "re.compile('" + reg_ex + "').fullmatch(output) != None"
        AtomicFunctionTest.__init__(self, parameters, correctness_test, messages, points, "Checks whether the returned string matches regular expression " + reg_ex + ".", pre_run_statements, post_run_statements)


class JudgmentCallFunctionTest(AtomicFunctionTest):
    """An atomic test for a function that needs human input to determine whether the function passed or not.  Yes to the question_to_ask (str) means the test passed."""
    def __init__(self, parameters, question_to_ask, test_code, messages, points, preRunStatements = [], postRunStatements = []):
        #these statements are to see whether the test has already passed.  If so, we don't want to be making the judgment call again!
        prepass_expression = "did_pass(eval(functionString).__name__, " + test_code + ", module.__name__)"
        #preprerun_statements = ["test_code = " + test_code, "function_to_test = eval(functionString)", "prepass = did_pass(function_to_test.__name__, test_code, module.__name__)", "prepass = True", "print('prepass:', prepass)"]
        #preRunStatements = preprerun_statements + preRunStatements
        #in case the test has already passed, put these statements in conditionals so they won't then get executed.
        #prestatements_together = "if (not prepass):"
        #for prestatement in preRunStatements:
        #    prestatements_together += "\n    " + prestatement
        #preprerun_statements.append(prestatements_together)
        #preRunStatements = preprerun_statements
        correctnessTest = "prepass or input(\"" + question_to_ask + " [y/N]\\n\").lower().startswith('y')"
        postRunStatements.append("if (not prepass) and passed:\n    save_pass(eval(functionString).__name__, " + test_code + ", module.__name__)")
        AtomicFunctionTest.__init__(self, parameters, correctnessTest, messages, points, "Asks the user whether a function should pass, then stores the result to shortcut in the future.", preRunStatements, postRunStatements)
        self.add_prepass_expression_as_string(prepass_expression)
  
def pass_file_exists(function_name, test_code):
    '''Checks to see that the pass file exists, and in a folder called 'judgmentCalls'.'''
    #store everything in a directory called judgmentCalls
    judgment_calls = Path("./judgmentCalls")
    if not judgment_calls.exists():
        judgment_calls.mkdir()
    
    #if the file doesn't exist, create it
    filename = 'judgmentCalls/' + function_name + '-' + test_code + '.txt'
    calls_file = Path("./" + filename)
    if not calls_file.exists():
        calls_file.touch()
        
        #give everyone read/write permissions
        calls_file.chmod(stat.S_IRUSR) #user can read it
        calls_file.chmod(stat.S_IWUSR) #user can write to it
        calls_file.chmod(stat.S_IRGRP) #group can read it
        calls_file.chmod(stat.S_IWGRP) #group can write to it
        calls_file.chmod(stat.S_IROTH) #others can read it
        calls_file.chmod(stat.S_IWOTH) #others can write to it
        
        calls_file.chmod(0o777)
    

def did_pass(function_name, test_code, module_name):
    """Checks a file, named by the function, to see whether the named module is listed as having completed that function."""
    #first, make sure the directory and file are set up correctly
    pass_file_exists(function_name, test_code)
    
    filename = 'judgmentCalls/' + function_name + '-' + test_code + '.txt'
    f = open(filename, 'r')
    passed = False
    for line in f:
        if line.startswith(module_name):
            passed = True
    f.close()
    #print('did_pass: ' + function_name + ", " + str(test_code) + ", " + str(passed), type(passed))
    return passed
    
    
def save_pass(function_name, test_code, module_name):
    """Writes to a file, named function_name, a new line with the given module_name, indicating that that module has passed the function test."""
    #first, make sure the directory and file are set up correctly
    pass_file_exists(function_name, test_code)
    
    filename = 'judgmentCalls/' + function_name + '-' + test_code + '.txt'
    f = open(filename, 'a')
    f.write(module_name + "\n")
    f.close()

#TODO: add these back in and make them appropriate!
#         except KeyboardInterrupt:
#             #We want to quit out if I say so!
#             timeSoFar = time.clock() - startTime
#             print '\nTaken', timeSoFar, 'seconds so far.'
#             quit = raw_input("Should I permanently exit? (y/N)\n")
#             if quit.lower() == 'y':
#                 raise KeyboardInterrupt
#             else:
#                 result = "Looks like this was running too long!"
#                 traceback.print_exc()
#         except ValueError:
#             #Hopefully this will only happen when testing a guardian.  TODO: check to make sure that's the case!!!
#             print "No guardian!"
#             result = "No Guardian!  Junk!"
#         except TypeError:
#             #Hopefully this will only happen when testing a guardian.  TODO: check to make sure that's the case!!!
#             print "No guardian!"
#             result = "No Guardian!  Junk!"
#         except:  #case where the function does not exist!
#             #TODO: does this case ever happen?
#             message = "This code does not run!"
#             traceback.print_exc()
#             self.results.append(["Function does not run!", 0])
        
class FunctionExistenceTest(FunctionTest):
    """Tests whether a function exists.  All other tests can be children of this test."""
    
    def __init__(self, passPoints, passSubtests, failPoints = 0, failSubtests = []):
        description = "Tests to see whether this function exists."
        isCalled = False
        parameters = ()
        correctnessTest = "isinstance(givenFunction, types.FunctionType) or isinstance(givenFunction, types.BuiltinFunctionType) or isinstance(givenFunction, types.MethodType)"
        passMessage = "This function exists."
        passPoints = passPoints
        passSubtests = passSubtests
        failMessage = "This function does not exist!  Perhaps you didn't name yours correctly?"
        failPoints = failPoints
        failSubtests = failSubtests
        preRunStatements = []
        postRunStatements = []
        FunctionTest.__init__(self, description, isCalled, parameters, correctnessTest, passMessage, passPoints, passSubtests, failMessage, failPoints, failSubtests, preRunStatements, postRunStatements) 

        
class RecursiveFunctionTest(FunctionTest):
    """A test that checks that a function is recursive."""
    
    def __init__(self):
        #correctness_test = "(givenFunction.__name__ + '(') in get_function_text(givenFunction)"
        correctness_test = "is_recursive(givenFunction) or has_recursive_helper(givenFunction)"
        FunctionTest.__init__(self, "Checks that the function is recursive.", False, [], correctness_test, "The function is recursive, good!", 1, [], "This function is supposed to be recursive, but it isn't!  You need to rewrite this function to be recursive!", 0, [], [], [])
      
        
class FunctionDocstringTest(FunctionTest):
    """Tests whether a function has a docstring.  It has no children and always deducts 3 points in the absence of a docstring."""
    
    def __init__(self, failPoints = -3):
        description = "Tests to see whether this function has a docstring."
        isCalled = False
        parameters = ()
        correctnessTest = "givenFunction.__doc__.strip() != ''"
        passMessage = ""
        passPoints = 0
        passSubtests = []
        failMessage = "This function does not have a valid docstring!"
        if (failPoints > 0):
            #ensure that the fail points is negative.  Seems like this could be a common error.
            failPoints = -1*abs(failPoints)
        failSubtests = []
        preRunStatements = []
        postRunStatements = []
        FunctionTest.__init__(self, description, isCalled, parameters, correctnessTest, passMessage, passPoints, passSubtests, failMessage, failPoints, failSubtests, preRunStatements, postRunStatements) 
        
class FunctionNullTest(FunctionTest):
    """This test always passes, and serves as a splitter for passing subtests."""
        
    def __init__(self, passSubtests):
        description = "A null test."
        isCalled = False
        parameters = ()
        correctnessTest = "True"
        passMessage = ""
        passPoints = 0
        passSubtests = passSubtests
        failMessage = ""
        failPoints = 0
        failSubtests = []
        preRunStatements = []
        postRunStatements = []
        FunctionTest.__init__(self, description, isCalled, parameters, correctnessTest, passMessage, passPoints, passSubtests, failMessage, failPoints, failSubtests, preRunStatements, postRunStatements) 
        
class FunctionGuardianTest(FunctionTest):
    """This test tries illegal inputs to make sure guardians are working."""
    
    def __init__(self, parameters, passPoints, guardingAgainst = "all incorrect inputs."):
        description = "Tests that the guardians are working."
        isCalled = True
        parameters = parameters
        correctnessTest = "output == None and len(printedOutput.strip()) > 0"
        passMessage = "Guardians work correctly, nice!"
        passPoints = passPoints
        passSubtests = []
        failMessage = "This function does not guard against " + guardingAgainst
        failPoints = 0
        failSubtests = []
        preRunStatements = []
        postRunStatements = []
        FunctionTest.__init__(self, description, isCalled, parameters, correctnessTest, passMessage, passPoints, passSubtests, failMessage, failPoints, failSubtests, preRunStatements, postRunStatements) 

class FunctionTestWrapper(object):
    """Wraps a function test.  Tests for existence, then runs all the tests in the given list."""
    
    def __init__(self, tests, maxPoints, functionName, alternateFunctionNames, className = None, isBonus = False):
        self.maxPoints = maxPoints
        self.functionName = functionName
        self.alternateFunctionNames = alternateFunctionNames
        self.className = className
        self.isBonus = isBonus
        #nullTest serves as a starting point for all other tests.  It is the root of the tree after existence/correct name has been established.
        self.nullTest = FunctionNullTest(tests)
        
    def getMaxPoints(self):
    	'''Returns the maximum amount of points earnable for this problem.'''
    	return self.maxPoints
    	
    def getPointsOutOf(self):
    	'''Returns the amount of points students are expected to attain to perfectly pass this problem.  (If it is a bonus problem, they don't have to do it at all!)'''
    	if self.isBonus:
    		return 0
    	else:
    		return self.getMaxPoints()
        
    def runTestsOnModule(self, module, part_number = 0):
        """Runs this test on the module, returning a PartResults object."""
        test_results = PartResults("Part " + str(part_number) + " - " + self.functionName)
        usedFunctionName = self.functionName
        #make a first run to see if it passes the existence test
        #existencePoints = min(10, self.maxPoints/2)
        existencePoints = self.maxPoints
        existenceTest = FunctionExistenceTest(0, [])
        existenceResults = existenceTest.runTestOnFunction(self.functionName, module, self.className)
        #print("existenceResults:", existenceResults)
        i = 0
        rootTest = FunctionExistenceTest(existencePoints, [self.nullTest])
        for alternateFunctionName in self.alternateFunctionNames:
            if existenceResults.full_credit():
                #we have already found this and don't need to keep going
                break
            else:
                print(str(existenceResults))
            usedFunctionName = alternateFunctionName
            existenceResults = existenceTest.runTestOnFunction(usedFunctionName, module, self.className)
            test_results.add_result("This function does not have the correct name.", -2, 0)
        if not existenceResults.full_credit():
            #couldn't find the function and no alternative names matched
            if self.isBonus:
                #The function is a bonus problem, so don't go searching for alternative names.  Let the students complain about their grades first!
                test_results.add_result("The function is not defined in your file.", 0, self.getPointsOutOf())
                return test_results
            print("")
            print("Module Name: " + module.__name__)
            print("Look for function: " + self.functionName)
            print("None of our alternatives worked, what did the student name the function?  (Which should be named: " + self.functionName + ")  Here are some other options:\n")
            if self.className == None:
                memberList = dir(module) 
            else:
                #TODO: figure out how to use this line correctly.  This is to display the methods for the class instead of just the functions in the file
                #memberList = dir(module.(eval(className)))
                memberList = dir(module)
            for memberName in memberList:
                if memberName[0] != '_':
                    print(memberName)
            print("\nAbove are member names in the student's file.")
            print("Look for function: " + self.functionName + "\n")
            newAlternativeName = input("Choose 'none' if no such function is defined.\n")
            if (newAlternativeName == 'none'):
                test_results.add_result("The function is not defined in your file.", 0, self.getPointsOutOf())
                return test_results
            else:
                usedFunctionName = newAlternativeName
                input("Add this to the list.  Please press Enter once you have done that!")
        #okay, now run the actual full tests
        test_results.add_results(rootTest.runTestOnFunction(usedFunctionName, module, self.className))
        return test_results
        
class EmptyWrapper(FunctionTestWrapper):
    """Wrapper for no tests.  Good for zero-point parts."""
    
    def __init__(self):
        """Creates an empty test wrapper"""
        FunctionTestWrapper.__init__(self, [], 0, "", [])
    
    def runTestsOnModule(self, module, partNumber = 0):
        """Returns no tests."""
        return PartResults() #Returns a new null part results
        


        
#These three classes are an attempt to set up gradeable items before grading them.  I'm not sure if this is a good idea, but here it is.
        
class GradeableItem(object):
    """Models the points earned on an assignment.  Could be a number or ungraded."""
    
    def __init__(self, full_points):
        self.full_points = full_points #the amount this is "out of"
        self.result = UngradedResult()
        
    def grade(self, points_earned, feedback):
        """Updates this to be graded with the given parameters."""
        self.result = GradedResult(points_earned, feedback)
        
    def __str__(self):
        return self.result.to_string(self.full_points)
    
    def got_full_credit(self):
        return self.result.get_earned_points() >= self.full_points
    
    
class UngradedResult(object):
    """Models an ungraded score."""
    
    def __init__(self):
        pass
    
    def __str__(self):
        return "ungraded"
    
    def to_string(self, full_points):
        return "Not yet graded."
    
    def get_earned_points(self):
        return 0
    
class GradedResult(object):
    """Models a graded score."""
    
    def __init__(self, score, feedback):
        self.score = score
        self.feedback = feedback
        
    def __str__(self):
        return str(self.score) + " points earned.  " + self.feedback
    
    def to_string(self, full_points):
        """Return a string version of this that uses the full points for 100%"""
        return str(self.score) + "/" + str(full_points) + "  " + self.feedback
    
    def get_earned_points(self):
        """Returns the number of points earned."""
        return self.score
        
        
        
        
        
#Objects describing the results of grading
        
class FunctionResults(object):
    """Wrapper to contain multiple FunctionResult objects."""
    
    def __init__(self):
        self.results = FunctionNullResults()
        
    def __str__(self, indent = ""):
        return self.results.__str__(indent)
        
    def get_earned_points(self):
        """Returns the total points earned."""
        return self.results.get_earned_points()
        
    def get_full_points(self):
        """Returns the number of points needed to earn 100%."""
        return self.results.get_full_points()
    
    def full_credit(self):
        """Returns whether this result has gotten full (or better) credit."""
        return self.results.get_earned_points() >= self.results.get_full_points()
        
    def everything_incorrect(self):
        """Returns whether all tests failed in this."""
        return self.results.everything_incorrect()
        
    def get_num_incorrect_parts(self):
        """Returns the number of incorrect parts in this."""
        return self.results.get_num_incorrect_parts()
        
    def add_results(self, other):
        """Adds another FunctionResults object to this."""
        self.add_result(other.results)
        
    def add_result(self, result):
        """Adds a FunctionResult object to this."""
        self.results = FunctionCompositeResults(self.results, result)
        
    def add_new_result(self, feedback, earned_points, full_points):
        """Adds a new result based on the provided parameters."""
        self.add_result(FunctionSingleResult(feedback, earned_points, full_points))

    
class FunctionResult(object):
    """Models the results of grading a single function."""
    
    def __init__(self):
        pass
        
    def __str__(self, indent = ""):
        raise Error("FunctionResults.__str__() should never be called directly!")
        
    def get_earned_points(self):
        """Gets the total points earned."""
        raise Error("FunctionResults.get_earned_points() should never be called directly!")
        
    def get_full_points(self):
        """Gets the points that this is "out of"."""
        raise Error("FunctionResults.get_full_points() should never be called directly!")
    
    def get_num_incorrect_parts(self):
        """Returns the number of incorrect parts.  Should be either zero or one."""
        if self.full_credit():
            return 0
        else:
            return 1
            
    def full_credit(self):
        """Returns whether the full number of points have been earned for this."""
        return self.get_earned_points() >= self.get_full_points()
    
        
class FunctionNullResults(FunctionResult):
    """Models the results of an empty part that doesn't need any printed feedback."""
    def __init__(self):
        pass
        
    def __str__(self, indent = ""):
        return ""
        
    def get_earned_points(self):
        return 0
    
    def get_full_points(self):
        return 0
    
    def everything_incorrect(self):
        return False
        
class FunctionSingleResult(FunctionResult):
    """Models a single result."""
    
    def __init__(self, feedback, earned_points, full_points):
        self.feedback = feedback
        self.earned_points = earned_points
        self.full_points = full_points
        
    def __str__(self, indent = ""):
        string = indent + self.feedback + " (" + str(self.get_earned_points()) + "/" + str(self.get_full_points()) + ")\n"
        return string
        
    def get_earned_points(self):
        return self.earned_points
        
    def get_full_points(self):
        return self.full_points
    
    def everything_incorrect(self):
        return self.get_earned_points() <= 0 and self.get_earned_points() < self.get_full_points()
        
class FunctionCompositeResults(FunctionResult):
    """Models a composite of two subresults summed together."""
    
    def __init__(self, left_result, right_result):
        self.left = left_result
        self.right = right_result
        
    def __str__(self, indent = ""):
        return self.left.__str__(indent) + self.right.__str__(indent)
        
    def get_earned_points(self):
        return self.left.get_earned_points() + self.right.get_earned_points()
        
    def get_full_points(self):
        return self.left.get_full_points() + self.right.get_full_points()
    
    def everything_incorrect(self):
        return self.left.everything_incorrect() and self.right.everything_incorrect()


class PartResults(object):
    """Manages aggregating results into one object.  This is the interface other classes should use when building results."""
    
    def __init__(self, name = ""):
        self.name = name
        self.results = FunctionResults()
        
    def __str__(self, indent=""):
        results_string = self.results.__str__(indent + "  ")
        if (results_string == ""):
            #the results are null, so we don't want to return anything
            return results_string
        else:
            return indent + self.name + ":\n" + results_string
    
    def set_name(self, name):
        self.name = name
        
    def get_name(self):
        return self.name
    
    def get_earned_points(self):
        return self.results.get_earned_points()
    
    def get_full_points(self):
        return self.results.get_full_points()
    
    def full_credit(self):
        return self.results.full_credit()
        
    def add_result(self, feedback, earned_points, full_points):
        self.results.add_new_result(feedback, earned_points, full_points)
        
    def add_results(self, results):
        """Adds a FunctionResults object to this."""
        self.results.add_results(results)
        
    def everything_incorrect(self):
        """Returns whether everything in here is incorrect."""
        return self.results.everything_incorrect()
    
    def get_num_incorrect_parts(self):
        """Returns the number of tests that failed."""
        return self.results.get_num_incorrect_parts()
    

    
class ProjectResults(object):
    """Models the results of grading an entire project."""
    
    def __init__(self, name):
        self.name = name
        self.part_results = [] #a list of PartResults objects
        
    def __str__(self, indent = ""):
        string = indent + self.name + ": (" + str(self.get_earned_points()) + "/" + str(self.get_full_points()) + ")\n"
        for result in self.part_results:
            string += result.__str__(indent + "  ")
        return string
        
    def get_earned_points(self):
        """Returns the number of points earned."""
        points = 0
        for result in self.part_results:
            points += result.get_earned_points()
        return max(0, points)
    
    def get_full_points(self):
        """Returns the number of points necessary for full credit."""
        points = 0
        for result in self.part_results:
            points += result.get_full_points()
        return max(0, points)
    
    def add_part_results(self, part_result):
        """Adds the result from a single part to this."""
        self.part_results.append(part_result)
        
    def get_num_incorrect_parts(self):
        """Returns the number of parts that are not fully correct."""
        incorrect_parts = 0
        for result in self.part_results:
            if not result.full_credit():
                incorrect_parts += 1
        return incorrect_parts
 
  
  
#Next parts grade a whole project for one or more students

class ProjectGrader(object):
    """Describes the tools necessary to grade a project."""
    
    def __init__(self, projectNumber, functionTesters):
        """Constructor.  functionTesters is a list of FunctionTest objects."""
        self.projectNumber = projectNumber
        self.functionTesters = functionTesters
        
    def set_function_tester(self, test_index, function_tester):
        """Sets a function tester of this at a specific index.  If it's beyond the number of function testers we have so far, this pads the different with EmptyWrappers."""
        while len(self.functionTesters) <= test_index:
            #pad with the null tester
            self.functionTesters.append(EmptyWrapper())
        self.functionTesters[test_index] = function_tester
        
    def getMaxPoints(self):
        """Returns the max number of points available in this project.  (Bonus problems count.)"""
        maxPoints = 0
        for functionTester in self.functionTesters:
            if functionTester != None:
                maxPoints += functionTester.getMaxPoints()
        return maxPoints
        
    def getNonBonusMaxPoints(self):
        """Returns the max number of points available in this project.  (Bonus problems DON'T count.)"""
        maxPoints = 0
        for functionTester in self.functionTesters:
            if functionTester != None:
                maxPoints += functionTester.getPointsOutOf()
        return maxPoints
        
    def testFunction(self, functionTester, module, partNumber):
        """Applies the test to the function.  Returns a PartResults object. functionTester is a FunctionTestWrapper object.  This does not modify previous_results, it just uses it in case the information is vital."""
        #print(functionTester)
        if functionTester == None:
            results = PartResults()
        else:
            try:
                #results becomes a PartResults object
                results = functionTester.runTestsOnModule(module, partNumber)
            #except KeyboardInterrupt:
            #    #We should probably throw another exception here!
            #    raise KeyboardInterrupt
            #    TODO: what's the best way to kill turtleworld here?
            except:
                results = PartResults("Part " + str(partNumber))
                #results.add_result("Your code for this part causes exceptions on some inputs!", 0, self.getNonBonusMaxPoints())
                results.add_result("Your code for this part causes exceptions on some inputs!", 0, functionTester.getPointsOutOf())
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print("Unexpected error:", sys.exc_info()[0], "more info:", sys.exc_info()[1])
                traceback.print_tb(sys.exc_info()[2])
                
        return results
    
    def apply_lateness(self, days_late, results):
        """Adds a deduction to results if the module is late."""
        if days_late > 0:
            days_late_deduction = 10 * days_late
            deduction_string = str(days_late) + ' days late'
            results.add_result(deduction_string, -days_late_deduction, 0)
            
    def apply_file_name_error(self, has_error, results):
        """Adds a deduction to results if the has_error (there is a file name error)."""
        if has_error:
            deduction_points = 2
            results.add_result("Incorrect filename", -deduction_points, 0)
        
    def gradeProject(self, module, fileNameError, daysLate = 0):
        """Grades the project, returning Results object."""
        project_results = ProjectResults("Project " + str(self.projectNumber))
        #check for common deductions
        self.apply_lateness(daysLate, project_results)
        self.apply_file_name_error(fileNameError, project_results)
        outOfPoints = self.getNonBonusMaxPoints()
        #grade all the parts in the project
        part_number = 0
        for functionTester in self.functionTesters:
            #grade a single part and incorporate the results
            function_results = self.testFunction(functionTester, module, part_number)
            #TODO: add a part here that just gives praise and full credit if they get everything right. :)
            project_results.add_part_results(function_results)
            part_number += 1
        return project_results
        
    def gradeClass(self, students, dropped = [], classSections = []):
        outOfPoints = self.getNonBonusMaxPoints()
        print("Student array: ", students)
        firstStudent = input("Who is the first student?  Please enter their username or just hit enter to start from the beginning.\n")
        writeOrAppend = 'a'
        i = 0
        if (firstStudent == '') : #starting from the beginning
            writeOrAppend = 'w'
        else :
            i = len(students) #set it to the end in case we make an error on the username, then we'll just jump to the end.
            for j in range(len(students)):
                if students[j][0] == firstStudent:
                    i = j
        onlyOnce = input("Would you like to only check this student? [y/N]   ") + "n"
        if onlyOnce.lower()[0] == 'y':
            onlyOnce = True
            daysLate = input("How many days late is this? (Hit Enter for none.)  ")
            if daysLate == "":
                daysLate = 0
            else:
                daysLate = int(daysLate)
        else:
            onlyOnce = False
            daysLate = 0
        gradesFile = open("project" + str(self.projectNumber) + "Grades.txt", writeOrAppend)
        gradesFile.write("***************** Grades for Project " + str(self.projectNumber) + " ******************\n\n")
        gradesFile.flush()
        grades = []
        #these are run in alphabetical order for Moodle
        while i < len(students):
            student = students[i] #student = [studentID, studentName]
            if not student[0] in dropped:
                gradesFile.write("" + student[1] + " \n")
                print("**~~~~~~~~~~~~~Grading " + student[1] + "'s Project~~~~~~~~~~~~~**\n")
                # old version: moduleName = student[0] + "_project" + str(self.projectNumber)
                moduleName = student[0] + "_projects"
                moduleLoaded = False
                syntaxErrored = False
                fileNameError = False
                while not moduleLoaded:
                    try:
                        module = __import__(moduleName)
                        moduleLoaded = True
                    except ImportError:
                        print("Error while importing!")
                        traceback.print_exc()
                        print("It looks like they didn't name their file correctly!  (No " + moduleName + ".py exists!)")
                        fileNameError = True
                        moduleName = input("What did they name their file?  (file name minus the '.py' or 'none' if they don't have one))\n")
                        if moduleName[-3:] == '.py':
                            moduleName = moduleName[0:len(moduleName)-3]
                        elif (moduleName == 'none'):
                            break
                    except:
                        print("Running failed: syntax or run-time (probably a name) error!")
                        traceback.print_exc()
                        studentResults = ['There is either a syntax error in the project or a run-time error outside of any function definitions!  Please fix your code and email it back to me!  The penalty for this is twice the regular lateness penalty (meaning 20 points lost per day instead of 10).  In the future, be sure to make sure your program runs directly before submitting.\n', '*'] # was ...\n', 0]  Will this work?
                        syntaxErrored = True
                        break
                if not moduleLoaded:
                    #TODO: apply an error here, they get a ZERO!
                    if not syntaxErrored:
                        studentResults = ["No project submitted!\nPlease email your project to me ASAP!\nTotal Score: 0/" + str(outOfPoints) + "\n",0]
                else:
                    studentResults = self.gradeProject(module, fileNameError, daysLate)
                gradesFile.write(str(studentResults))
                gradesFile.write("\n\n")
                gradesFile.flush()
            else:
                #the student has dropped the course in this case.
                #TODO: turn this into a ProjectResults object
                studentResults = ["Dropped the course!", 0]
            grades.append([student[1], studentResults.get_earned_points()])
            if onlyOnce: #we only wanted the one student, so stop going!
                break
            i += 1
        
        #write the section A ones, for the spreadsheet
        for section in classSections:
            gradesFile.write('Spreadsheet grades for one of the sections:\n')
            for student in students:
                if student[0] in section:
                    for grade in grades:
                        if grade[0] == student[1]:
                            gradesFile.write(grade[0] + ": " + str(grade[1]) + "\n")
            gradesFile.write('\n')
        gradesFile.flush()
            
        print("Nice job grading!")
        return grades
        
class HaltingProjectGrader(ProjectGrader):
    """Represents a project grader that stops grading after some errors have been found.  The remainder of the project is worth zero points."""
    
    def __init__(self, projectNumber, functionTesters):
        """Creates a new Project Grader for a given project number and a list of FunctionTestWrappers."""
        ProjectGrader.__init__(self, projectNumber, functionTesters)
        self.num_errors = 0
        
    def set_num_errors(self, errors):
        self.num_errors = errors
        
    def set_max_errors(self, max_errors):
        self.max_errors = max_errors
        
    def increment_num_errors(self):
        self.num_errors += 1
        
    def testFunction(self, functionTester, module, partNumber):
        """Refuses to test the function if there have already been too many errors."""
        if (self.num_errors < self.max_errors):
            #Not enough errors yet; keep going!
            part_results = ProjectGrader.testFunction(self, functionTester, module, partNumber)
            
            #see whether that part was incorrect
            if not part_results.full_credit():
                self.increment_num_errors()
                #print("num_errors:", self.num_errors)
            
            #Now return the results
            return part_results
        else:
            #create and return the too-many-errors result
            #print("Too many errors!  Can't keep going!")
            errored_out = PartResults("Part " + str(partNumber))
            errored_out.add_result("Errored out!", 0, functionTester.getPointsOutOf())
            return errored_out
        
    def gradeProject(self, module, fileNameError, daysLate = 0):
        """Grades the project.  Halts if it gets to too many failures.  Currently: daysLate is ignored.  Returns a triple: (feedback, pointsEarned, failuresLeft)"""
        #use a field to keep track of the failures remaining
        #self.set_max_errors(failuresRemaining)
        results = ProjectGrader.gradeProject(self, module, fileNameError, daysLate)
        #reset the num_errors
        self.num_errors = 0
        return results

#Next part grades multiple projects for one student         
            
class HaltingModuleGrader(object):
    """Grades all projects in a module, but halts when it's encountered too many errors."""
    
    def __init__(self, graders, maxFailures = 1):
        """Creates a new grader for all projects.  """
        self.graders = graders
        self.maxFailures = maxFailures
        
    def num_projects(self):
        """Returns the number of Project Graders in this.  (This should be the number of projects.)"""
        return len(self.graders)
        
    def getNonBonusMaxPoints(self):
        """Returns the total (non-bonus) points that can be earned from all graders."""
        points = 0
        for project_grader in self.graders:
            points += project_grader.getNonBonusMaxPoints()
        return points
        
    def grade(self, module):
        """Grades all projects for a single file.  Returns a tuple: (feedback, points).  Assumes that all project solutions are in the same file."""
        num_failures = 0
        feedback = ""
        points = 0
        for projectGrader in self.graders:
            failuresRemaining = self.maxFailures - num_failures
            feedback += "Allowed errors (remaining): " + str(failuresRemaining) + "\n"
            projectGrader.set_max_errors(failuresRemaining)
            
            results = projectGrader.gradeProject(module, False, 0) #grade the next project
            num_failures += results.get_num_incorrect_parts()
            feedback += str(results)
            points += results.get_earned_points()
            if num_failures >= self.maxFailures:
                break
        feedback += "\n~~~~~~~~\nTotal Grade: " + str(points) + "/" + str(self.getNonBonusMaxPoints()) + "\n~~~~~~~~"
        return (feedback, points)
        
    def grade_modules(self, modules):
        """Grades all modules.  Returns a dictionary: modules -> pairs: (feedback, points)."""
        grades = dict()
        for module in modules:
            grades[module] = self.grade(module)
        return grades

#Next: grade all projects for all students

def gradeAndOutput(moduleGrader, students, grades_file):
    """Outputs grades to the given file.  students is a list of tuples: (name as "Last, First...", username).  Each module is named "usernameProjects"."""
    feedback = "Grades up through Project " + str(moduleGrader.num_projects()-1) + ":\n"
    summary = ""
    maxPoints = moduleGrader.getNonBonusMaxPoints()
    for student in students:
        feedback += "\n***** Begin " + student[0] + " *****\n"
        moduleName = student[1] + "_projects"
        try:
            module = __import__(moduleName)
            result = moduleGrader.grade(module)
        except ImportError as e:
            if e.msg.startswith("No module named '" + moduleName):
                result = ("Unable to find your file.  There is no file named " + moduleName + ".py", 0)
            else:
                result = ("Your code doesn't run because there was a problem importing your file: " + e.msg, 0)
        except Exception as e:
            result = ("Importing your file caused an error:\n" + str(e), 0)
            #traceback.print_exc()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        feedback += result[0]
        summaryResult = student[0] + ": " + str(result[1]) #+ "\n"
        summary += summaryResult + "\n"
        feedback += "\n***** End " + student[0] + " *****\n\n\n"
        print(summaryResult + "/" + str(maxPoints))
    grades_file.write(feedback + "\nSummary:\n" + summary)
    grades_file.flush()
    print("Nice job grading!")



      
#practice tests
def main():
    fiveTest = FunctionTest("Tests whether this returns 5.", True, (), "output == 5", "This function works correctly.", 40, [], "This function does not return 5.", 0, [])
    existTest = FunctionExistenceTest(10, [fiveTest])
    printTest = FunctionTest("Tests whether this prints 5.", True, (), "printedOutput.strip() == '5'", "This function works correctly.", 40, [], "This function does not print '5'.", 0, [])
    existTest1 = FunctionExistenceTest(10, [printTest])


if __name__ == "__main__":
    prefix = get_whitespace_prefix(" \t  heading")
    print("'" + prefix + "'")
    print(get_function_text(get_whitespace_prefix))
    print("In the zone, monkeys!")
    functions = get_functions(get_function_text)
    print("Functions found:")
    for function in functions:
        print(function.__name__)
    main()

            
                    
                    
                    
        
