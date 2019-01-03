# PythonProjectGrader
A grader for assignments written in Python 3.x

This automatically grades projects and spits out the results with a Command-Line Interface.  (There is no GUI version.)

The user needs to provide a key for all projects, as well as the tests, in a file keysAndTests.py.  A sample keysAndTests.py is provided here, with examples of the different test options.

Two sample submitted files are included: kwburke_projects.py and jwdoe_projects.py.  One has many errors; one has only one error.

Example Python code to actually run the grader is included in RunGrader.py.  Users will have to modify this to meet their own needs.

To immediately test everything that's included as-is:

$ python3 RunGrader.py 0

Then look at project0Grades.txt for the output.

