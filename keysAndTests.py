'''Sample File containing the keys and tests for the PythonProjectGrader.
   Author: Kyle Burke <kwburke@plymouth.edu>'''

import math
import sys
from ProjectGrader import *

docstring_test = FunctionDocstringTest(1) #use this like a singleton

recursive_test = RecursiveFunctionTest() #use this like a singleton

######### add_five (FruitfulFunctionTest and FunctionTestWrapper) ##################

#First, the function:

def add_five(number):
    '''Returns number + 5.'''
    return number + 5

#Now let's write some tests:  (I've made these very verbose to highlight the meaning of each variable.)
inputs = [100]
solution = 105
correct_feedback = "Works with big numbers, great!"
incorrect_feedback = "Doesn't really work with big numbers."
correct_points = 3
incorrect_points = 0
add_five_test_0 = FruitfulFunctionTest(inputs, solution, [correct_feedback, incorrect_feedback], [correct_points, incorrect_points])

inputs = [-5]
solution = 0
correct_feedback = "Works with negative numbers, good!"
incorrect_feedback = "Doesn't work with negative numbers."
correct_points = 2
incorrect_points = 0
add_five_test_1 = FruitfulFunctionTest(inputs, solution, [correct_feedback, incorrect_feedback], [correct_points, incorrect_points])

#Now wrap all the tests into a single object, the FunctionTestWrapper
total_points = 5
function_name = "add_five"
common_misspellings = ["ad_five", "add_5", "addfive"]
add_five_tester = FunctionTestWrapper([add_five_test_0, add_five_test_1], total_points, function_name, common_misspellings)

#after students have learned about docstrings, I make them write a docstring each time by putting the docstring test on the beginning of this.  It makes sure they write (non-empty) docstrings.  It's not super useful, but it works:

add_five_tester = FunctionTestWrapper([docstring_test, add_five_test_0, add_five_test_1], total_points, function_name, common_misspellings)



############## print_greeting (PrintingFunctionTest, PrintingRegularExpressionTest) #################

#Many of my early projects just involve printing to the screen instead of returning values, so I needed a way to handle them.  Here's an example of that.

def print_greeting(name):
    '''Prints a greeting to someone.'''
    print("Hi, " + str(name) + "!")
    

#Here's a test that checks the printed output.  (The interface is exactly the same, it's just a different object.)
inputs = ["'Monkey'"]  #The inputs will be evaluated, so put string inputs inside two sets of quotes.  This string will evaluate to the string 'Monkey'.
solution = "Hi, Monkey!"
correct_feedback = "Passes the monkey test, excellent!"
incorrect_feedback = "Fails the monkey test"
correct_points = 4
incorrect_points = 0
print_greeting_test_0 = PrintingFunctionTest(inputs, solution, [correct_feedback, incorrect_feedback], [correct_points, incorrect_points])

#Alternatively (or additionally) you might want to be more lenient on the printed output using regular expressions.  Here's an example of doing that.
inputs = ["'BoJimbo'"]
solution = "[Hh]i,? BoJimbo!?"
correct_feedback = "Uses the correct words (though not necessarily the punctuation/capitalization)."
incorrect_feedback = "This doesn't print the right words."
correct_points = 6
incorrect_points = 0
print_greeting_test_1 = PrintingRegularExpressionTest(inputs, solution, [correct_feedback, incorrect_feedback], [correct_points, incorrect_points])

#Then you can wrap these up like the others.
total_points = 10
function_name = "print_greeting"
common_misspellings = ["greeting", "print_greting", "printgreeting"]
print_greeting_tester = FunctionTestWrapper([print_greeting_test_0, print_greeting_test_1], total_points, function_name, common_misspellings)





############# Point (AtomicFunctionTest) ###################

#Sometimes we need to create objects, call methods on them, then test properties.  AtomicFunctionTest is the way to do this!


#Here's the key for a basic Point class.

class Point(object):
    """Represents a point in 2 dimensions."""
    
    def __init__(self, x, y):
        """Initializes this point."""
        self.x = x
        self.y = y
        
    def __str__(self):
        """Returns a string version of this."""
        return "(" + str(x) + ", " + str(y) + ")"
    
    def __eq__(self, other):
        """Returns whether this equals other."""
        return self.x == other.x and self.y == other.y


#first, let's just test that the __init__ method works.
#important: if an error occurs during execution, then the incorrect stuff with happen
inputs = ["p", "3", "5"]
correctness_test = "True"  #this is always going to succeed if the method completes
correct_feedback = "No errors encountered while __init__ ran, that's good!"
incorrect_feedback = "The __init__ method caused an exception!"
correct_points = 6
incorrect_points = 0
pre_run_statements = ["p = module.Point(0, 0)"]  #These are lines of code to execute before running the actual test.  Notice that we need to do this because we need to create p as it's one of the inputs.  'module' is the variable referring to the module with the students' code
point_init_test = AtomicFunctionTest(inputs, correctness_test, [correct_feedback, incorrect_feedback], [correct_points, incorrect_points], preRunStatements = pre_run_statements)

#we can build the wrapper like before, except we need to include the class as part of the name of the method.

total_points = 6
function_name = "Point.__init__"
common_misspellings = []  #I don't include these, because they really shouldn't get this wrong; it's a special method.
point_init_tester = FunctionTestWrapper([docstring_test, point_init_test], total_points, function_name, common_misspellings)




#TODO: add an example of how to do Judgement-Call tests.  In order to make these tests, we will store the result once it's done correctly so we don't have to ask anymore.  In order to do this, each judgment call function needs to have a separate test code, which should be something that evaluates to a unique string.  (But it also needs to be the same every time, so no random generation.)

import turtle

def draw_square(turtle):
    '''Draws a square with a given turtle.'''
    for i in range(4):
        turtle.fd(100)
        turtlel.lt(90)
    

inputs = ["raphael"]
correctness_question = "Did raphael draw the square?  (In blue and with sides of 100.)"
test_code = "'0'"  #The test code needs to evaluate to a string, so again with the double quotes.
correct_feedback = "Works perfectly!"
incorrect_feedback = "Doesn't work."
correct_points = 5
incorrect_points = 0
#these statements create the turtle, set the pen color to blue (so you know it was raphael that drew it, and not a separate turtle), and draw a nearby marker 100 units long to show the correct distance
pre_run_statements = ["import turtle", "turtle.clearscreen", "raphael = turtle.Turtle()", "raphael.pencolor('blue')", "raphael.fd(100)", "raphael.lt(90)", "raphael.fd(6)", "raphael.bk(12)", "raphael.fd(6)", "raphael.lt(90)", "raphael.fd(100)", "raphael.rt(90)", "raphael.bk(6)", "raphael.fd(12)", "raphael.penup()", "raphael.fd(14)", "raphael.pendown()", "raphael.rt(90)"]
post_run_statements = ["turtle.clearscreen()"]
raphael_draw_square_test_0 = JudgmentCallFunctionTest(inputs, correctness_question, test_code, [correct_feedback, incorrect_feedback], [correct_points, incorrect_points], pre_run_statements, post_run_statements)

total_points = 5
function_name = "draw_square"
common_misspellings = []
raphael_draw_square_tester = FunctionTestWrapper([docstring_test, raphael_draw_square_test_0], total_points, function_name, common_misspellings)
