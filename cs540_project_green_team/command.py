"""This class represents a command, all parsed out and ready to execute.
It serves as the interface layer between the natural language processing
(which mostly happens in patterns.py) and actual execution or reporting
on the world state (which mostly happens in main.py).

Anything our agent can do, can be represented as one or more Command
objects."""

import random

class ObjectSpec(object):
    def __init__(self):
        # block color, if specified (NOTE: always uppercase!)
        self.color = None        
        
        # block ID, if specified
        self.id = None
        
        # how the block was referred to (explicitly or implicitly); this
        # is usually "block", but could be "wildcard" (if that was explicitly
        # used in testing), or a pronoun like "it", "them", or "one".
        self.block = "block"
        
        # True if plural; False if singular; None if unspecified
        self.plural = None        
        
        # True if definite ("the"/"those"); False if indefinite ("any/a");
        # None if unspecified
        self.definite = None  
    
        # Color of the block, if specified
        self.color = None
    
        # if the block was specified only by a location, then this is it:
        self.location = None

        # Number of block for count related operations
        self.block_count = -1
        
        #Dimension for making rows
        self.dim = random.choice("xy")
    
    def __str__(self):
        if self.id != None: return self.block + str(self.id)
        s = ''
        if self.block_count >= 0: s = str(self.block_count) + ' '
        s += self.block
        if self.color != None: s = self.color + " colored " + s
        if self.plural and s[-1].lower()!='s': s += "s"
        if self.definite: s = "the " + s
        if self.location != None: s = s + " " + str(self.location)
        return s

class Location(object):
    def __init__(self):
        # x value, if specified
        self.column = None
        
        # y value, if specified
        self.row = None
        
        # z (height above the table), if specified
        self.height = None
        
        # relation, if given: 'on-top-of', 'side-by-side'
        self.relation = None
        
        # ObjectSpec of the block that self.relation is relative to
        self.relativeTo = None

    def __str__(self):
        if self.row or self.column or self.height:
            return "in location %d %d %d" % (self.column, self.row, self.height)
        if self.relation:
            return self.relation + " " + str(self.relativeTo)
        return "?[Invalid location]"
        
class AbsoluteLocation(object):
	def __init__(self, id):
		self.id = id
		
	def __str__(self):
		return "absolute location "+str(self.id)
		
class Wildcard(object):
	def __init__(self, id):
		self.id = id
		
	def __str__(self):
		return str(self.id)

class Command(object):
    def __init__(self, action, obj=None, loc=None, dim=None):
        self.action = action        # action to carry out: 'put', 'count', etc.
        self.object = obj           # ObjectSpec of object(s) to act on
        self.location = loc         # target location

    def __str__(self):
        s = self.action
        if self.object: s += " " + str(self.object)
        if self.location: s += " " + str(self.location)
        return s

def run_tests():
    x = ObjectSpec()
    x.id = 42
    assert str(x) == "block42"
  
    x = ObjectSpec()
    x.color = "red"
    assert str(x) == "red block"
    x.plural = True
    assert str(x) == "red blocks"
    x.definite = True
    assert str(x) == "the red blocks"

    loc = Location()
    loc.relation = 'on-top-of'
    loc.relativeTo = ObjectSpec()
    loc.relativeTo.id = 2
    assert str(loc) == "on-top-of block2"
    
    x = ObjectSpec()
    x.location = loc
    x.definite = True
    assert str(x) == "the block on-top-of block2"

    loc = Location()
    loc.column = 1
    loc.row = 2
    loc.height = 0
    assert str(loc) == "in location 1 2 0"
    

if __name__ == "__main__":
    run_tests()
    print("Tests complete.")
