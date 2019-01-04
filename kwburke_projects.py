'''Project File for Kyle Burke.  (This file has lots of errors to demonstrate the grader.)
   author: Kyle Burke <kwburke@plymouth.edu>'''
   
def add_five(number):
    return number + 4

def print_greeting(name):
    print("Hi, Monkey!")
    

class Point(object):
    
    def __init__(x, y): #left off self on purpose
        self.x = x
        self.y = y
    
    
def draw_square(turtle):
    '''Draws a square with a given turtle.'''
    for i in range(3):
        turtle.fd(100)
        turtle.lt(90)
