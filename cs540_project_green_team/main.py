import os
import argparse
import copy
import math
import plot.plot

# Uncomment just one of the following to choose a visualizer:
#from plot import plot as vis
from dummyVis import dummyVis as vis

from PathPlanner.PathPlanner import *
from Parser.Parser import Parser
from Parser.ParseUtils import *
from command import *
import time
from datetime import timedelta
import stanfordnlp
from stanfordnlp.utils.resources import DEFAULT_MODEL_DIR
import _thread
import patterns

LOCALHOST = '127.0.0.1'
PORT = 65432

animation_delay_sec = 1.5
lang_model_dir = DEFAULT_MODEL_DIR
pp = PathPlanner()

initial_state = None
goal_state = None
start_state = None
recent_objspec = None
nextWildcardNum = 1

# Conditionally set global variables to default value
if True:
    initial_state = "examples/initialState/ex2-start.txt"
    goal_state = "examples/goals-PA2/ex2-goal.txt"
    start_state = pp.initializeStartState(initial_state)


def do_put(obj_spec, location):
    # Put an object described by the given ObjectSpec, into a place satisfying Location
    global pp
    global initial_state
    global start_state

    start_time = time.time()

    path_planner = PathPlanner()

    # Prepare a move as a 3-element list:
    #    object to move
    #    relation or command
    #    target or object
    move = [None, None, None]

    # We're going to have to make this fancier, but for now, let's just
    # pick any object that satisfies the given obj_spec, and do the same
    # for the location.relativeTo.
    possible_objects = find_objects(obj_spec)
    if len(possible_objects) == 0:
        print("I can't find any " + str(obj_spec) + ".")
        return
    move[0] = possible_objects[0].id
    print("Chose", move[0], "from", possible_objects, "to satisfy", obj_spec)
    
    if location.relation is None:
        print("I don't know how to move to " + str(location) + ".")
        return
    move[1] = location.relation

    possible_relations = find_objects(location.relativeTo)
    if len(possible_relations) == 0:
        print("I can't find any " + str(location.relativeTo) + ".")
        return

    for r in possible_relations:
       if r.id != move[0]:
          move[2] = r.id
          break
    print("Chose", move[2], "from", possible_relations, "to satisfy", location.relativeTo)

    if move[2] is None:
       print("I can't find target object")
       return

    return move

def do_stack(obj_spec, goal):
    global start_state, nextWildcardNum

    print("do_stack(", obj_spec, ")")   # for debugging
    objs = find_objects(obj_spec)
    count = len(objs)
    if obj_spec.plural and obj_spec.block_count <= 0:
        # if no count was specified, the implied count is "all"
        obj_spec.block_count = count
    if count == 0:
        print("There are no such blocks.")
        return
    if count < obj_spec.block_count:
        if count == 1:
            print("There is only one such block,", )
        else:
            print("There are only", count, "such blocks,", 
                "so I can't stack up", obj_spec.block_count, "of them.")
        return
        
    # Specify a tower using a wildcard for each block, with one
    # on the table, and the others above that in a stack.
    colorProp = None
    if obj_spec.color is not None: colorProp = ('color', obj_spec.color.lower())
    print("obj_spec is ", obj_spec, " so colorProp is ", colorProp)
    
    w = "wildcard" + str(nextWildcardNum)
    goal.addRequirement(w, "above", "table")
    if colorProp is not None: goal.addRequirement(w, "has", colorProp)
    nextWildcardNum += 1
    
    for i in range(1, obj_spec.block_count):
        w = "wildcard" + str(nextWildcardNum)
        goal.addRequirement(w, "above", "wildcard" + str(nextWildcardNum-1))
        if colorProp is not None: goal.addRequirement(w, "has", colorProp)
        nextWildcardNum += 1
        if i == obj_spec.block_count-1:
            goal.addRequirement("nothing", "above", w)

def do_row(obj_spec, goal):
    global start_state, nextWildcardNum

    print("do_row(", obj_spec, ")")   # for debugging
    objs = find_objects(obj_spec)
    count = len(objs)
    if obj_spec.block_count <= 0:
        # no object count given; assume 1 or all, depending on plurality
        obj_spec.block_count = (count if obj_spec.plural else 1)
    if count == 0:
        print("There are no such blocks.")
        return
    print("Making a row of", count, "blocks.")
    if count < obj_spec.block_count:
        if count == 1:
            print("There is only one such block,", 
                 "so I can't line up", obj_spec.block_count, "of them.")
        else:
            print("There are only", count, "such blocks,", 
                "so I can't line up", obj_spec.block_count, "of them.")
        return
        
    # Specify a row using a wildcard for each block, with one
    # given only color (if specified), and the others next to that in succession.
    colorProp = None
    if obj_spec.color is not None: colorProp = ('color', obj_spec.color.lower())
      
    if colorProp is not None:
        goal.addRequirement("wildcard" + str(nextWildcardNum), "has", colorProp)
        nextWildcardNum += 1
    
    goal.addRequirement("wildcard" + str(nextWildcardNum-1), "next-to-"+obj_spec.dim, "nothing")
    for i in range(1, obj_spec.block_count):
        w = "wildcard" + str(nextWildcardNum)
        goal.addRequirement(w, "next-to-"+obj_spec.dim, "wildcard" + str(nextWildcardNum-1))
        if colorProp is not None: goal.addRequirement(w, "has", colorProp)
        nextWildcardNum += 1
        if i == obj_spec.block_count-1:
            goal.addRequirement("nothing", "next-to-"+obj_spec.dim, w)

def do_clear(obj_spec, goal):
    print("do_clear(", obj_spec, ")")  # for debugging
    objs = find_objects(obj_spec)
    print("objects found: ", objs);
    count = len(objs)
    if obj_spec.block_count <= 0:
        # no object count given; assume 1 or all, depending on plurality
        obj_spec.block_count = (count if obj_spec.plural else 1)
    if count == 0:
        print("There are no such blocks.")
        return
    if count < obj_spec.block_count:
        if count == 1:
            print("There is only one such block,", 
                 "so I can't clear off", obj_spec.block_count, "of them.")
        else:
            print("There are only", count, "such blocks,", 
                "so I can't clear off", obj_spec.block_count, "of them.")
        return
    for i in range(0, obj_spec.block_count):
        goal.addRequirement("nothing", "above", objs[i].id)
    
def do_move(obj, location):
    global start_state

    #Object - Target Location
    move = [None, None, None]

    move[0] = obj.id
    move[1] = "at"


    pLoc = Location()
    if location.row != -1:
       pLoc.row = location.row
    else:
       pLoc.row = start_state.blocks[move[0]].x

    if location.column != -1:
       pLoc.column = location.column
    else:
       pLoc.column = start_state.blocks[move[0]].y

    # If the location is occupied, stack it
    for h in range(0, 10):
        pLoc.height = h
        if start_state.spaceIsOpen(pLoc.row, pLoc.column, pLoc.height):
            move[2] = (pLoc.row, pLoc.column, pLoc.height)
            break

    if move[2] is None:
       return None
    else:
       return move[0],move[1],move[2]


def find_objects(obj_spec):
    # Return a list of all the blocks satisfying the given object spec.
    
    if obj_spec.block == "WILDCARD" and obj_spec.id is not None:
        # given a specific object ID, just find that object
        return [Wildcard(obj_spec.block+str(obj_spec.id))]
        
    if obj_spec.id is not None:
        # given a specific object ID, just find that object
        b = start_state.blocks.get("block" + str(obj_spec.id))
        if b is None:
            return []
        return [b]

    # If we have a reference to a previous spec, make use of that
    if obj_spec.block in ["IT", "THEM", "ONE", "ONES", "THAT", "THOSE"]:
        # OK, user has given us something like "it" or "the blue one".
        # We need to recall the previous object spec, and then apply
        # any specifics (like color) given with the new one.
        if recent_objspec == None:
            print("I don't know what you're referring to.")
            return []
        x = copy.copy(recent_objspec)
        if obj_spec.color is not None:
            x.color = obj_spec.color    # e.g. "the blue one"
        elif x.color is not None:
            obj_spec.color = x.color
        obj_spec = x
        print("Anaphora resolved to: " + str(obj_spec))

    # If we're asking for a location
    if obj_spec.location is not None:
        return [AbsoluteLocation(obj_spec.location)]

    # If not given a specific ID, then find blocks that satisfy the criteria.
    # For now, the only criteria we support is color.
    result = []
    for blk_id in start_state.blocks:
        blk = start_state.blocks[blk_id]
        if obj_spec.color is None or blk.properties.get('color').upper() == obj_spec.color:
            result.append(blk)
    return result


def get_requirement(cmd, goal):
    # Deal with the given Command. 
    # This may include adding requirements to the given goal.
    global recent_objspec
    
    if cmd is None:
        return
    if cmd.action == 'pickup':
        print("We can't just pick things up yet.")
    elif cmd.action == 'put':
        move = do_put(cmd.object, cmd.location)
        if move:
            goal.addRequirement(*move)

    elif cmd.action == 'move':
        objs = find_objects(cmd.object)

        if len(objs) == 0:
            print("Move - I can't find any " + str(objs) + ".")
            return

        print("Found: ", objs)

        firstFoundObject = objs[0]

        obj,rel,location = do_move(firstFoundObject, cmd.location)

        if location is None:
            print("No Valid Locations to Move To.")
        else:
            #goal.addRequirement(firstFoundObject, "at", (cmd.location.row, cmd.location.column, cmd.location.height))
            goal.addRequirement(obj,rel,location)


    elif cmd.action == 'count':
        objs = find_objects(cmd.object)
        count = len(objs)
        if count == 0:
            print("There are no such blocks.")
        else:
            print("I find " + str(count) + " such block" + 's' * (count != 1) + ".")
    elif cmd.action == 'identify' or cmd.action == 'find':
        objs = find_objects(cmd.object)
        count = len(objs)
        if count == 0:
            print("There are no such blocks.")
        else:
            goal.set_highlight_property(objs)
            if count == 1:
                print("That is block " + objs[0].shortId() + ".")
            elif count == 2:
                print("Those are blocks " + objs[0].shortId() + " and " + objs[1].shortId() + ".")
            else:
                print("Those are blocks " + ", ".join(map(lambda o:o.shortId(), objs[:-1])) +
                    ", and " + objs[-1].shortId() + ".")
    elif cmd.action == 'locate':
        objs = find_objects(cmd.object)
        count = len(objs)
        if count == 0:
            print("There are no such blocks.")
        else:
            goal.set_highlight_property(objs)
            if count == 1:
                print("Block " + objs[0].shortId() + " is at " + objs[0].locationStr() + ".")
            elif count == 2:
                print("They are at " + objs[0].locationStr() + " and " + objs[1].locationStr() + ".")
            else:
                print("They are at " + "; ".join(map(lambda o:o.locationStr(), objs[:-1])) +
                      "; and " + objs[-1].locationStr() + ".")

    elif cmd.action == 'stack' or cmd.action == 'tower':
        do_stack(cmd.object, goal)

    elif cmd.action == 'row':
        do_row(cmd.object, goal)

    elif cmd.action == 'clear':
        do_clear(cmd.object, goal)
        
    else:
        print("I don't know how to do a '" + cmd.action + "' action yet.")
    
    # now, if we got a block reference that isn't itself anaphora, store it
    # so future anaphora can be resolved
    if cmd.object and cmd.object.block[:5] == "BLOCK":
        recent_objspec = cmd.object

def take_actions(goal):
    global pp
    global initial_state
    global start_state
    
    if goal is None: return

    print("Initial goal:")
    print(goal)
    
    goal.finalize()
    
    print("Finalized goal:")
    print(goal)
    
    start_time = time.time()

    backtrace, visited_states, start_state = pp.a_star(start_state, goal)
    movePlanner = MovePlanner(backtrace)
    moves, visited_states = movePlanner.plan(skipRelease=False)

    elapsed = str(timedelta(seconds=time.time() - start_time))
    for m in moves:
        print(m[0])
        vis.show_state(m[1], m[0])
        time.sleep(animation_delay_sec)
    if len(moves) != 0:
        vis.show_state(start_state, m[0])
        print("Completed move planning in {0} moves after visiting {1} unique states in {2}".format(
           str(len(moves)), str(visited_states), elapsed))
    else:
       tmp_start_state = copy.deepcopy(start_state)
       for block in goal.blocks:
          if 'highlight' in goal.blocks[block].properties:
             tmp_start_state.blocks[block].setProperty('highlight', True)
       vis.show_state(tmp_start_state)

    # Wait for one second then show the final state
    # This clears block highlights/selections
    time.sleep(1)
    vis.show_state(start_state)

def demo_nlp():
    global start_state
    print("StanfordNLP")
    print("Please stand by while we initialize the StanfordNLP pipeline...")
    global lang_model_dir
    pipeline = stanfordnlp.Pipeline(models_dir=lang_model_dir, lang='en', use_gpu=False)
    print()
    print("Enter sentence(s) to parse, or just press Return to exit.")
    while True:
        inp = input("Input: ")
        if inp == "": return
        if inp == "PLOT":
            plot.plot.present(start_state)
            continue

        inp = preprocess(inp)
        doc = pipeline(inp)

        goal = Requirements(start_state)
        for i in range(0, len(doc.sentences)):
            cmd = patterns.handle_input(doc.sentences[i])
            get_requirement(cmd, goal)

        take_actions(goal)

        if recent_objspec:
            print("recent_objspec:", recent_objspec)


def demo_path_planner():
    global pp
    global initial_state
    global start_state
    global animation_delay_sec
    start_time = time.time()

    # Initialize to global variable
    demo_initial_state = initial_state

    # If global variable was not set, use a default value
    if not is_valid_file(demo_initial_state):
        demo_initial_state = "examples/initialState/Gorbett-start1.txt"

    # Create initial state
    start_state = pp.initializeStartState(demo_initial_state)
    # NOTE: State is an object that contains a dictionary, state.blocks, in the form {blockid: blockObject}
    # The blockObject should contain all the information necessary to visualize it

    # Create a planner for individual moves
    path_planner = PathPlanner()
    # Display the initial state
    # vis.show_state(start_state)

    # Get moves to put block5 on the table in the given state
    print("------------------------------")
    print("planMove - block5 above table")
    print("------------------------------")
    new_state, moves, visited_states = path_planner.planMove(("block5", "above", "table"), start_state)
    elapsed = str(timedelta(seconds=time.time() - start_time))

    for move in moves:
        print(move[0])
        vis.show_state(move[1], move[0])
        time.sleep(animation_delay_sec)

        # Print final state w/o command.  This is needed to 'remove' command formatting
        vis.show_state(move[1])

    print("Completed move planning in {0} moves after visiting {1} unique states in {2}".format(
        str(len(moves)), str(visited_states), elapsed))

    # Get moves to put slide block4 next to block6
    print("--------------------------------------")
    print("planMove - slide block4 next to block6")
    print("--------------------------------------")
    start_time = time.time()
    new_state, moves, visited_states = path_planner.planMove(("block4", "next-to", "block6"), new_state)
    elapsed = str(timedelta(seconds=time.time() - start_time))

    for move in moves:
        print(move[0])
        vis.show_state(move[1], move[0])
        time.sleep(animation_delay_sec)

        # Print final state w/o command.  This is needed to 'remove' command formatting
        vis.show_state(move[1])

    print("Completed move planning in {0} moves after visiting {1} unique states in {2}".format(
        str(len(moves)), str(visited_states), elapsed))


def setup():
    # Get parameters from command line
    parser = argparse.ArgumentParser(description='CS540 FinalProject Green Team')
    parser.add_argument('-m', '--model_dir', help='Path to model directory')
    parser.add_argument('-i', '--init_state', help='Path to initial state file')
    parser.add_argument('-g', '--goal_state', help='Path to goal state file')
    # Use the following lines if we want the initial state passed in as command line argument
    # required_args = parser.add_argument_group('required named arguments')
    # required_args.add_argument('-i', '--initial_state', help='Initial state file name', required=True)

    args = parser.parse_args()

    # Define global variables so this function can update them
    global lang_model_dir
    global initial_state
    global goal_state

    if args.model_dir:
        lang_model_dir = args.model_dir
    if args.init_state:
        initial_state = args.init_state
    if args.goal_state:
        goal_state = args.goal_state


def is_valid_file(file_name, show_msg=False):
    if file_name is None:
        if show_msg:
            print("WARNING: No file name given")
        return False

    if not os.path.exists(file_name):
        if show_msg:
            print("ERROR: File does not exist")
        return False

    if not os.path.isfile(file_name):
        if show_msg:
            print("ERROR: File does not exist")
        return False

    return True


def set_initial_state():
    global initial_state
    global start_state
    global pp
    print("Enter initial state file: ")
    file = os.path.abspath(input())
    if is_valid_file(file, True):
        initial_state = file
        print("Set initial state file - {}".format(initial_state))
        start_state = pp.initializeStartState(initial_state)
        vis.show_state(start_state)


def set_goal_state():
    global goal_state
    print("Enter goal state file: ")
    file = os.path.abspath(input())
    if is_valid_file(file, True):
        goal_state = file
        print("Set goal state file - {}".format(goal_state))


def print_menu_and_take_action():
    os.system('clear')
    print("CS540 Green Team Project")
    print("  1. Set initial state file")
    print("  2. Set goal state file")
    print("  3. Run Path Planner")
    print("  4. Demo NLP")
    print("  0. Exit")

    choice = input()
    if choice == "1":
        set_initial_state()
    if choice == "2":
        set_goal_state()
    if choice == "3":
        demo_path_planner()
    if choice == "4":
        demo_nlp()
    if choice == "0":
        return False

    print("Press Return to continue")
    input()
    return True


def input_thread():
    # give the main thread time to get setup (to avoid any initialization warnings)
    time.sleep(1)

    # Main processing loop
    run = True
    while run:
        # entry = input(':')
        # response = handle_input(entry)
        # print(response)
        run = print_menu_and_take_action()

    vis.stop()
    exit(0)


def main():
    global pp
    global initial_state
    global start_state

    # Get the start state if initial_state is defined and valid
    if is_valid_file(initial_state, False):
        start_state = pp.initializeStartState(initial_state)

    if vis.blocksMainThread():
        # Start the input thread, and then show the visualization
        # window on the main thread
        _thread.start_new_thread(input_thread, ())
        vis.present(start_state)
    else:
        # If our visualizer doesn't need to block the main thread,
        # then just invoke our input loop directly
        input_thread()


if __name__ == "__main__":
    # Read input from command line and set global variables if necessary
    setup()

    # Start main processing loop
    main()
