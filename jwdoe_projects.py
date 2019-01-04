'''Project File for Jane Doe.  (This file has only one error.)
   author: Jane Doe'''
   
   
   
   
########### Project 1 below ###################
    

class Point(object):
    '''Models a point object.
    attributes: x, y.'''
    
    def __init__(self, x, y): 
        '''Constructor'''
        self.x = x
        self.y = y
       
   
def draw_square(turtle):
    '''Draws a square with a given turtle.'''
    for i in range(4):
        turtle.fd(100)
        turtle.lt(90)
   
   
   
########### Project 0 below ###################
   
def add_five(number):
    return number + 5

def print_greeting(name):
    '''Prints a nice greeting.'''
    print("Hi,", str(name) + "!")
    
