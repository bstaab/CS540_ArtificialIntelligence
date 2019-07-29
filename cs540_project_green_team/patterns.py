from Parser.ParseUtils import *
from command import *
import re

handlers = []

colors = ["red", "green", "blue", "orange", "yellow", "purple", "aqua"]

def tree_to_objspec(tree):
    """Study the given parse tree, which should be some sort of block description,
    and build a corresponding ObjectSpec."""
    result = ObjectSpec()
    result.block = tree.text

    if result.block.lower() in colors:
        result.block = "BLOCK"
        result.color = tree.text


    if tree.text[:5] == "BLOCK" and tree.text[5:].isdigit():
        # simple case: we got a named block
        result.id = int(tree.text[5:])
        result.block = "BLOCK"
        return result
    if tree.text[:8] == "WILDCARD" and tree.text[8:].isdigit():
        # another simple (though quite unlikely) case: we got a named wildcard
        result.id = int(tree.text[8:])
        result.block = "BLOCK"
        return result

    # Sometimes SNLP sticks the color in as the head.  THAT'S annoying.
    # Check for that and sort it out.
    if tree.text in ['RED','YELLOW','GREEN','BLUE','PURPLE','CYAN','ORANGE']:
        result.color = tree.text
        result.text = "BLOCK"

    # Otherwise, we have a block described by its attributes.
    # Dig down in this tree to find stuff we can use, like
    # 'compound' or 'amod' words, which are usually colors.
    for kid in tree.children:
        if kid.dependency_relation == "case" and (kid.text == "AT" or kid.text == "TO"): #If location is a tuple
            tup = [c for c in tree.text if c.isdigit()]
            if len(tup) >= 3:
                result.location = (int(tup[0]),int(tup[1]),int(tup[2]))
        if kid.dependency_relation == 'amod' and kid.text.lower() == 'half':
            result.block_count = 'half'
        elif kid.dependency_relation == 'amod' or kid.dependency_relation == 'compound':
            # ToDo: do we ever see amod/compound that is NOT a color? 
            # If so, we might want to check for kid.text in a list of valid colors.
            result.color = kid.text
        if kid.dependency_relation == 'det':
            if kid.text == 'the' or kid.text == 'that' or kid.text == 'those':
                result.definite = True
            if kid.text == 'a' or kid.text == 'any':
                result.definite = False
            if kid.text.lower() == 'all':
                result.block_count = 'all'
        if kid.dependency_relation == 'nummod':
           result.block_count = int(kid.text)
    result.plural = (tree.text in ["BLOCKS", "ONES", "THEM", "THOSE"])
    return result

case_to_preposition = {
    'ATOP' : 'above',
    'ON' : 'above',
    'BESIDE' : 'next-to',
    'UNDER' : 'under',
    'IN' : 'at',
    'TO' : 'at',
    'MOVE' : 'put',
}

def tree_to_location(tree):
    # check for a 'case' relation, which generally gives the preposition
    result = Location()
    for kid in tree.children:
        if kid.dependency_relation == 'case':
            result.relation = case_to_preposition.get(kid.text, kid.text.lower())
            break
    if result.relation == None:
        # Uh-oh... we're not prepared to handle this kind of location yet
        print("??? Unknown location: " + tree_to_string(tree))
        return None

    result.relativeTo = tree_to_objspec(tree)
    return result

class Handler:
    def __init__(self):
        self.patterns = []
    
    def add(self, patternStr):
        self.patterns.append(string_to_tree(patternStr))
    
    def match(self, inputTree):
        for pat in self.patterns:
            #print("Matching:", tree_to_string(inputTree), "against", tree_to_string(pat))
            m = tree_match(inputTree, pat)
            #print("Result:", m)
            if m is not None: return m
        return None
    
    def handle(self, match):
        print(type(self).__name__ + ' matched, but no `handle` method defined')

#----------------------------------------------------------------------
class PickUpHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        #self.add("[PICK compound:prt[UP] obj[$1]]")
        self.add("[LIFT obj[$1]]")
        self.add("[GRAB obj[$1]]")

    def handle(self, match):
        obj = tree_to_objspec(match['$1'])
        return Command('pickup', obj)

handlers.append(PickUpHandler())       
#----------------------------------------------------------------------
class PutLocationHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.add("[PUT obj[$1] obl[$2]]")
        self.add("[PICK compound:prt[UP] obj[$1] conj[PUT punct[$3] cc[$4] obj[$5] obl[$2]]")
    
    def handle(self, match):
        obj = tree_to_objspec(match['$1'])
        loc = tree_to_location(match['$2'])
        tree = match['$2']

        if tree.text[:3] == "ROW":
            loc = Location()
            for kid in tree.children:
                if kid.dependency_relation == "nummod":
                    loc.row = int(kid.text)

            loc.column = -1
            loc.height = -1
            return Command('move', obj, loc)

        elif tree.text[:6] == "COLUMN":
            loc = Location()
            for kid in tree.children:
                if kid.dependency_relation == "nummod":
                    loc.column = int(kid.text.replace('.',''))

            loc.row = -1
            loc.height = -1
            return Command('move', obj, loc)

        else:
           match_obj = re.match(r'(\d),(\d)', tree.text)
           ignore_obj = re.match(r'(\d),(\d),(\d)', tree.text)
           if match_obj and not ignore_obj:
              loc = Location()
              loc.row = int(match_obj.group(1))
              loc.column = int(match_obj.group(2))
              loc.height = -1
              return Command('move', obj, loc)
              
        return Command('put', obj, loc)

handlers.append(PutLocationHandler())


# ----------------------------------------------------------------------
class MoveLocationHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.add("[MOVE obj[$1] obl[$2]]")

    def handle(self, match):

        print("\nMatch 1:\n", match['$1'])

        obj = tree_to_objspec(match['$1'])

        loc = Location()

        tree = match['$2']

        # Handle Specified Row case here
        if tree.text[:3] == "ROW":

            for kid in tree.children:
                if kid.dependency_relation == "nummod":
                    loc.row = int(kid.text)

            loc.column = -1
            loc.height = -1

        elif tree.text[:6] == "COLUMN":

            for kid in tree.children:
                if kid.dependency_relation == "nummod":
                    loc.column = int(kid.text.replace('.',''))

            loc.row = -1
            loc.height = -1

        else:
           match_obj = re.match(r'(\d),(\d)', tree.text)
           if match_obj:
              loc.row = int(match_obj.group(1))
              loc.column = int(match_obj.group(2))
              loc.height = -1

        return Command('move', obj, loc)


handlers.append(MoveLocationHandler())

#----------------------------------------------------------------------
class StackUpHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.add("[STACK compound:prt[UP] obj[$1]")
        #[STACK compound:prt[UP] obj[BLOCKS nummod[TWO] compound[BLUE]]]

    def handle(self, match):
        obj = tree_to_objspec(match['$1'])
        return Command('stack', obj)

handlers.append(StackUpHandler())

#----------------------------------------------------------------------
class TowerHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        #[MAKE obj[TOWER det[A] nmod[BLOCKS case[OF]]] punct[,] parataxis[HIGH nummod[4]]]
        #[MAKE obj[TOWER det[A] nmod[BLOCKS case[OF] compound[RED] punct[,]] appos[HIGH nummod[3]]]]
        self.add("[MAKE obj[TOWER nmod[$1] parataxis[$2]]]")
        self.add("[MAKE obj[TOWER nmod[$1] appos[$2]]]")
        self.add("[MAKE obj[TOWER nmod[$1] nmod[$2]]]")
        self.add("[MAKE obj[TOWER det[A] nmod[BLOCKS case[OF] compound[RED]] nmod[HIGH nummod[3]]]]")
        #[MAKE obj[TOWER det[A] punct[,] appos[HIGH nummod[3]]]]
        self.add("[MAKE obj[TOWER] parataxis[$2]")
        self.add("[MAKE obj[TOWER] appos[$2]")
        #[MAKE obj[HIGH det[A] compound[TOWER] nummod[3]]]
        self.add("[MAKE obj[HIGH det[A] compound[TOWER] nummod[$2]]]")
        self.add("[MAKE obj[HIGH det[A] compound[TOWER nmod[$1]] nummod[$2]]]")

    def handle(self, match):
        if '$1' in match:
            obj = tree_to_objspec(match['$1'])
        else:
            obj = ObjectSpec()
            obj.block = "BLOCK"
        
        try:
            obj.block_count = int(match['$2'].text)
        except:
            pass
        if obj.block_count <= 0:
            nummod = find_subnode(match.get('$2'), 'nummod')
            if nummod is None: nummod = find_subnode(match.get('$1'), 'nummod')
            print("attempt to find nummod returned:", tree_to_string(nummod) if nummod else "None")
            if nummod is not None:
                obj.block_count = int(nummod.text)
                
        return Command('tower', obj)

handlers.append(TowerHandler())

#----------------------------------------------------------------------
class RowHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        #[MAKE obj[ROW det[A] nmod[BLOCKS case[OF] nummod[4] amod[RED]]]]
        self.add("[MAKE obj[ROW nmod[$1]]]")
        #[MAKE obj[ROW det[A] nmod[BLOCKS case[OF] amod[RED]]] advmod[LONG nummod[4]]]
        self.add("[MAKE obj[ROW nmod[$1]] advmod[$2]]")

    def handle(self, match):
        if '$1' in match:
            obj = tree_to_objspec(match['$1'])
        else:
            obj = ObjectSpec()
            obj.block = "BLOCK"
        
        try:
            obj.block_count = int(match['$2'].text)
        except:
            pass
        if obj.block_count <= 0:
            nummod = find_subnode(match.get('$2'), 'nummod')
            if nummod is None: nummod = find_subnode(match.get('$1'), 'nummod')
            print("attempt to find nummod returned:", tree_to_string(nummod) if nummod else "None")
            if nummod is not None:
                obj.block_count = int(nummod.text)
                
        return Command('row', obj)

handlers.append(RowHandler())

#----------------------------------------------------------------------
class ClearHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.add("[CLEAR obj[$1]]")
        self.add("[CLEAR obl[$1]]")

    def handle(self, match):
        obj = tree_to_objspec(match['$1'])
        return Command('clear', obj)

handlers.append(ClearHandler())


#----------------------------------------------------------------------
class FindHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.add("[FIND obj[$1]]")
        self.add("[NOTE obj[$1]]")
        self.add("[NOTICE obj[$1]]")
        self.add("[TAKE obj[NOTE nmod[$1]]")

    def handle(self, match):
        return Command('find', tree_to_objspec(match['$1']))

handlers.append(FindHandler())       
#----------------------------------------------------------------------
class CountHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.add("[COUNT obj[$1]]")
        self.add("[THERE nsubj[$1 amod[MANY advmod[HOW]] amod[$2]] cop[ARE]]")
        # This one causes problems because it is too general:
        #self.add("[$2 nsubj[$1 amod[MANY advmod[HOW]]] cop[ARE]]")

    def handle(self, match):
        if '$2' in match:
            # with these patterns, $1 is the item type (e.g. BLOCKS)
            # and $2 is the attribute (generally a color)
            obj = ObjectSpec()
            obj.color = match['$2'].text
        else:
            # otherwise, it's a standard block description phrase
            obj = tree_to_objspec(match['$1'])
        if obj.block == "MANY": obj.block = "THEM" # (happens with "how many are there")
        return Command('count', obj)
        
handlers.append(CountHandler())       
#----------------------------------------------------------------------
class IdentifyHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.add("[IDENTIFY obj[$1]]")
        self.add("[NAME obj[$1]]")
        self.add("[WHAT cop[IS] nsubj[$1]]")
        self.add("[WHAT cop[ARE] nsubj[$1]]")

    def handle(self, match):
        return Command('identify', tree_to_objspec(match['$1']))

handlers.append(IdentifyHandler())       
#----------------------------------------------------------------------
class LocateHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.add("[LOCATE obj[$1]]")
        self.add("[WHERE cop[IS] nsubj[$1]]")
        self.add("[WHERE cop[ARE] nsubj[$1]]")

    def handle(self, match):
        return Command('locate', tree_to_objspec(match['$1']))

handlers.append(LocateHandler())       
#----------------------------------------------------------------------

def get_command(inputTree):
    for h in handlers:
        match = h.match(inputTree)
        if match is not None:
            # For now, we'll just let the FIRST handler handle it.
            # We may need to do something fancier later.
            cmd = h.handle(match)
            print("==>", cmd)
            return cmd
    return None

def handle_input(stanfordSentence):
    """Parse the input; return a Command."""
    inputTree = sentence_to_tree(stanfordSentence)
    print(tree_to_string(inputTree))        # (for debugging)

    cmd = get_command(inputTree)
    if cmd is not None: return cmd
    print("I don't have a handler for:")    
    print(tree_to_string(inputTree))

def test_input(stringTree):
    """Take the given sentence in string-tree form, and ensure that it matches a pattern."""
    inputTree = string_to_tree(stringTree)
    for h in handlers:
        match = h.match(inputTree)
        if match is not None:
            print(stringTree)
            x = []
            for k in match:
                x.append("'" + k + "': " + tree_to_string(match[k]))
            print("==>", "{" + ", ".join(x) + "}", "\n")
            return match
    print(tree_to_string(inputTree))
    print("**> NO MATCH!\n")

def run_tests():
    test_input("[MAKE obj[TOWER det[A] nmod[BLOCKS case[OF]]] punct[,] parataxis[HIGH nummod[3]]]")
    test_input("[MAKE obj[HIGH det[A] compound[TOWER] nummod[3]]]")
    test_input("[MAKE obj[TOWER det[A] punct[,] appos[HIGH nummod[3]]]]")
    test_input("[MAKE obj[TOWER det[A] nmod[BLOCKS case[OF] compound[RED] punct[,]] appos[HIGH nummod[3]]]]")

    cmd = get_command(string_to_tree("[MAKE obj[TOWER det[A] nmod[BLOCKS case[OF] compound[RED]] nmod[HIGH nummod[3]]]]"))
    print(cmd)
    cmd = get_command(string_to_tree("[MAKE obj[TOWER det[A] nmod[BLOCKS case[OF] compound[RED] punct[,]] appos[HIGH nummod[3]]]]"))
    print(cmd)

if __name__ == "__main__":
    run_tests()
