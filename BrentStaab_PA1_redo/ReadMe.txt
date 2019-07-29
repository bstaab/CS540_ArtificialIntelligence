Brent Staab
CS540: Artificial Intelligence - Spring 2019
Programming Assignment #1

This program was written and tested in Python3.6
To test the program
1) unzip bstaab_pa1.zip
2) cd to unzipped folder
3) run script 
    example: 'python ./PA1.py -i initial_state.txt -g goal_state.txt'
    
    NOTES:
    * The '-h' option displays help information
      'python ./PA1.py -h'
    
4) The output is written to the terminal.  
   It consists of a sequence of commands, one per line.
   The first (top) line is the first command executed.

5) The zip file containes a few test configurations that I used for devlopment/verification
    a) to run these tests, just change the -i and -g parameters
    b) the input and output files must be consistent
        - python ./PA1.py -i c1_initial.txt -g c1_goal.txt
    c) The corresponding path_[#]_block.txt file contains the steps used to reach the goal
       and the amound of time it took to find the goal.

NOTES:
1) The input file expects a single property or relation per line 
2) The program was tested in both Linux and Windows 
   - Python automatically handles Windows/Linux new line characters
3) This program does not implement much in the way of parameter validation.  If given more time,
   assumptions and requirements could be explicitly validated.  If anything improper were detected,
   the program should behave properly but this was not implemented.

