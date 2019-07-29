import re

def preprocess(text):
    '''Do our standard preprocessing to make StanfordNLP work a little better.'''
    # Uppercase it... just makes our lives easier to standardize
    text = text.upper()
    # Change e.g. "block 5" to "block5"
    text = re.sub(r'BLOCK (\d+)\b', r'BLOCK\1', text)
    # Change "place" to "put" since that seems to work much better
    text = re.sub(r'\bPLACE\b', 'PUT', text)
    # Change "on top of" to "atop", and "next to" to "beside", because these
    # single-word versions produce a better parse 
    text = re.sub(r'\bON TOP OF\b', 'ATOP', text)
    text = re.sub(r'\bNEXT TO\b', 'BESIDE', text)
    text = re.sub(r'\bNEXT-TO\b', 'BESIDE', text)
    # Standardize synonyms we might get for "block"
    text = re.sub(r'\bITEM\b', 'BLOCK', text)
    text = re.sub(r'\bCUBE\b', 'BLOCK', text)
    text = re.sub(r'\bBOX\b', 'BLOCK', text)
    text = re.sub(r'\bITEMS\b', 'BLOCKS', text)
    text = re.sub(r'\bCUBES\b', 'BLOCKS', text)
    text = re.sub(r'\bBOXES\b', 'BLOCKS', text)
    # Convert spelled-out numbers to numerals
    text = re.sub(r'\bZERO\b', '0', text)
    text = re.sub(r'\bONE\b', '1', text)
    text = re.sub(r'\bTWO\b', '2', text)
    text = re.sub(r'\bTHREE\b', '3', text)
    text = re.sub(r'\bFOUR\b', '4', text)
    text = re.sub(r'\bFIVE\b', '5', text)
    text = re.sub(r'\bSIX\b', '6', text)
    text = re.sub(r'\bSEVEN\b', '7', text)
    text = re.sub(r'\bEIGHT\b', '8', text)
    text = re.sub(r'\bNINE\b', '9', text)
    text = re.sub(r'\bMOVE\b', 'PUT', text)
    
    text = re.sub(r'\bIN\b', 'AT', text)
    text = re.sub(r'\bCLEAR BLOCK', 'CLEAR OFF BLOCK', text)
    
    # Work around a bizarre StanfordNLP bug that parses "count them"
    # as [THEM aux[COU] advmod[NT]] (but "count those" works fine):
    if text == "COUNT THEM": text = "COUNT THOSE"
    
    return text

def sentence_to_tree(sentence):
    '''Convert a StanfordNLP sentence object into a Word tree.'''
    # Each entry in sentence.dependencies is a 3-tuple, where index 2 is
    # a Word object containing the info we need.  In particular, it contains
    # text (the word itself), governor (the 1-based index of the parent), and 
    # dependency_relation ('root', 'det', 'amod', 'obj', etc).
    #
    # We're going to add a children list, so we can crawl this tree top-down.
    #print(sentence.dependencies)
    words = list(map(lambda d:d[2], sentence.dependencies))
    for w in words: w.children = []
    root = None
    for w in words:
        parent_idx = w.governor
        if parent_idx > 0: words[parent_idx-1].children.append(w)
        if w.dependency_relation == 'root': root = w
    # And then return the root.
    return root

def tree_to_string(w, label='', maxdepth=10):
    '''Return the subtree based at w, as a string.'''
    s = label + '[' + w.text.upper()
    if maxdepth > 0:
        for kid in w.children:
            s = s + ' ' + tree_to_string(kid, kid.dependency_relation, maxdepth-1)
    return s + ']'


class MinimalWord:
    def __init__(self, text=''):
        self.text = text
        self.dependency_relation = ''
        self.children = []

def close_brace_index(text, open_index):
    i = open_index+1
    open_count = 0
    while i < len(text):
        if text[i] == '[': open_count += 1
        if text[i] == ']':
            open_count -= 1
            if open_count < 0: return i
        i += 1
    # Close brace not found!
    return -1
    
def string_to_tree(text):
    '''Build a StanfordNLP-ish word tree from the given text.'''
    # Note that the result is not actually StanfordNLP words, but just little
    # objects that have .text, .dependency_relation, and .children.  So it's
    # compatible with what sentence_to_tree gives us, as well as print_tree.
    if text[0] != '[' or text[-1] != ']': raise ValueError('text should begin and end with square brackets')
    result = MinimalWord()
    spacePos = text.find(' ')
    if spacePos < 0:
        # this is a leaf node containing JUST the text of a word.
        result.text = text[1:-1]
        return result
    result.text = text[1:spacePos]
    # We got the text, now we need to find the children.  Each one
    # has the form: relation[node]
    pos = spacePos+1
    while pos < len(text):
        openPos = text.find('[', pos)
        relation = text[pos:openPos]
        closePos = close_brace_index(text, openPos)
        kid = string_to_tree(text[openPos:closePos+1])
        kid.dependency_relation = relation
        result.children.append(kid)
        pos = closePos + 2
    return result

def tree_match(fullTree, patternTree):
    '''Match patternTree against fullTree.  If it matches, return a map of named subtrees.'''
    # Example: given this full tree:
    #   [PUT obj[BLOCK det[THE] amod[RED]] obl[TOP case[ON] nmod[ONE case[OF] det[THE] amod[BLUE]]]]
    # ...and this pattern:
    #   [PUT obj[$1] obl[$2]]
    # Then it should match, and return a map like:
    #       '$1': [BLOCK det[THE] amod[RED]]
    #       '$2': [TOP case[ON] nmod[ONE case[OF] det[THE] amod[BLUE]]]
    # (with those values as Word trees, not strings).  Note that the match tags like $1
    # and $2 above can be anything, but must start with '$'.
    # If the pattern doesn't match, then we return None.
    #print("Matching " + tree_to_string(fullTree) + " against " + tree_to_string(patternTree))
    result = {}
    if patternTree.text[0] == '$':
        #print("Hmm... looks like the root here is a $ item:", patternTree.text)
        result[patternTree.text] = fullTree
    elif patternTree.text != fullTree.text:
        #print("Bailing out at root because " + patternTree.text + " != " + fullTree.text)
        return None  # root text doesn't match
    #print('text', patternTree.text, 'matches')
    fullKids = fullTree.children[:]
    for patKid in patternTree.children:
        #print("looking for child to satisfy", tree_to_string(patKid))
        satisfied = False
        for k in fullKids:
            #print("considering", k.dependency_relation, "for", tree_to_string(patKid))
            if k.dependency_relation != patKid.dependency_relation: continue
            #print('found possible matching kid for', tree_to_string(patKid))
            if patKid.text[0] == '$':
                #print('storing match for', tree_to_string(patKid))
                result[patKid.text] = k
                fullKids.remove(k)
                satisfied = True
                break
            else:
                #print('need to delve deeper for', tree_to_string(patKid))
                submatch = tree_match(k, patKid)
                if submatch == None:
                    #print("this kid's no good because submatch == None")
                    continue    # failure deeper in the tree
                #print('looks like this kid is good!')
                result.update(submatch)
                satisfied = True
                break
            break
        if not satisfied:
            #print("Bailing out because we couldn't find a matching kid for", tree_to_string(patKid))
            return None  # required child not found
    return result

def find_subnode(tree, relation):
    """Find a sub-tree within the given tree linked by the given dependency relation."""
    if tree is None: return None
    for kid in tree.children:
        if kid.dependency_relation == relation: return kid
        x = find_subnode(kid, relation)
        if x is not None: return x
    return None

def print_matches(d):
    for key in d:
        print(key, ':', tree_to_string(d[key]))

def run_tests():
    s = '[PICK obj[BLOCK det[THE] amod[RED]] compound:prt[UP]]' # "pick the red block up"
    print("Original:", s)
    tree = string_to_tree(s)
    print("As tree: ", tree_to_string(tree))
    pat = string_to_tree('[PICK compound:prt[UP] obj[$1]]')
    print("Matching:", tree_to_string(pat))
    match = tree_match(tree, pat)
    print_matches(match)

    print()
    s = '[RED nsubj[BLOCKS amod[MANY advmod[HOW]]] cop[ARE]]' # "how many blocks are red"
    print("Original:", s)
    tree = string_to_tree(s)
    print("As tree: ", tree_to_string(tree))
    pat = string_to_tree('[$2 nsubj[$1 amod[MANY advmod[HOW]]] cop[ARE]]')
    print("Matching:", tree_to_string(pat))
    match = tree_match(tree, pat)
    print_matches(match)

if __name__ == "__main__":
    run_tests()
    print("Tests complete.")

    
