"""Actual file to run the grader.
   Author: Kyle W Burke (kwburke@plymouth.edu)
E.g. to grade project (e.g.) 1:
$ python3 RunGrader 1   (use python3 for machines with default python 2)
To grade just one student:
$ python3 RunGrader 1 kgb1013 
"""

import sys
from keysAndTests import *
# projectNumber = 0
# 
# #create the grader!
# 
# grader = ProjectGrader(projectNumber, [None, printTest, nixTest, printAnswers])
# 
# grades = grader.gradeClass(students, dropped, classSections)

#create a list to hold all the individual project grader objects
project_graders = []

#create the grader for Project 0
project_number = 0
testers = [] #I set this to be empty initially, then add them later.  That's because...
grader = ProjectGrader(project_number, testers)

#... the set_function_tester method will fill in empty spaces with blank tests (in case you add optional/0-point/narrative parts to your projects like I do).
part = 3
tester = add_five_tester  #defined in keysAndTests.py
grader.set_function_tester(part, tester)

part = 5
tester = print_greeting_tester
grader.set_function_tester(part, tester)

project_graders.append(grader) #add the grader to the list



#Project 1
grader = ProjectGrader(1, [])  #I stopped with the verbose parameters for this one

grader.set_function_tester(7, point_init_tester)

project_graders.append(grader)


#... add more project graders in here...


def main():
    """Create the Grader and run it."""

    #I make our students submit all their code in a file named <username>_projects.py.  So, each pair here is a (name, username).
    
    #all students
    students = [("kwburke", "Kyle Burke"), ("jwdoe", "Jane Doe")]
    
    #grades_file = open("grades.txt", 'w') #The grader writes the output to this file
    
    max_students = len(students)
    
    num_projects = len(project_graders)
    
    project_num = 0
    
    #handle the command-line arguments
    print("Command line arguments:", sys.argv)
    
    #try to get the max project number from the command-line
    if len(sys.argv) > 1:
        try:
            project_num = int(sys.argv[1])
            print("I'm going to grade Project ", project_num)
        except:
            print("Couldn't get the project number.")
            print('sys.argv: ', sys.argv)
            
    #try to get the specific file from the command-line
    if len(sys.argv) > 2:
        student_file_prefix = sys.argv[2]
        print("Looks like you want to only grade: " + student_file_prefix + "_projects.py")
        #less_students = [student_file_prefix]
        less_students = []
        #if this is a student in our list, use the full information.  If they're not, then less_students will be empty after this loop
        for student in students:
            if student[1] == student_file_prefix:
                less_students.append(student)
        if less_students == []:
            #the student was not in the list.  Create a dummy student pair
            less_students = [("??? ????", student_file_prefix)]
        #grades_file.close()
        #grades_file = open("grades.txt", 'a')  #If I'm only grading one person, I usually want to just add that to the end of the grading file instead of replacing the whole thing.
        students = less_students
        
    #Now make sure the Key is first, for good measure  (I've commented this out, but I recommend you actually create the key file.)
    #students = [("Key", "key")] + students    
    
    print("I'm going to try to grade " + str(len(students)) + " file(s).")
        
        
    grader = project_graders[project_num]
    #run the grader, outputting to projectXGrades.txt
    grader.gradeClass(students)

    #grades_file.close()

if __name__ == '__main__':
    main()
