import argparse
import copy
import aStar
import block as b
import math
import time


# Function to setup/initialize the block world.
# The initial and goal states will be read from a file passed into the script
# ArgumentParser enforces that a value is passed in for each required parameter
# NOTE: I am not explicitly validating that the files exist, downstream file
#       operations will fail if they are not valid
def setup(initial_state_data, goal_state_data):
    parser = argparse.ArgumentParser(description='CS540: Programming Assignment #1 - Block world using A* search')
    required_args = parser.add_argument_group('required named arguments')
    required_args.add_argument('-i', '--initial_state', help='Initial state file name', required=True)
    required_args.add_argument('-g', '--goal_state', help='Goal state file name', required=True)
    args = parser.parse_args()

    # Get initial and goal state data from files and store explicit information in corresponding variables.
    # Next, post process the state and fill in all implied relationships.
    b.get_state_from_file(args.initial_state, initial_state_data)
    b.gen_relationships(initial_state_data)
    b.get_state_from_file(args.goal_state, goal_state_data)
    b.gen_relationships(goal_state_data)

    # Make sure initial and goal state blocks have the same colors
    for blk in initial_state:
        if initial_state[blk].color is not None:
            goal_state[blk].color = initial_state[blk].color
        elif goal_state[blk].color is not None:
            initial_state[blk].color = goal_state[blk].color


# Function to determine if a given state is the goal state
def block_world_goal_test(state, goal):
    return state == goal



# Function to determine all possible moves/commands for a given state.
def block_world_actions(state):
    step_cost = 1
    actions = []

    # stack command
    # The preconditions are that either|neither block has a block on top of it
    # Put id1 on top of id2 (command stack block-id1 block-id2).
    # Put id1 on table (command stack block-id1 table).
    for blk in list(state):
        # 'stack' only possible for top block (i.e. below == None)
        if state[blk].below is None:
            # If this block has neighbors, use table to separate
            if state[blk].height > 0 or len(state[blk].side_by_side) > 0:
                actions.append(('(command stack {} table)'.format(blk), step_cost))

            # Find all other blocks that this one can be stacked on
            for inner_blk in list(state):
                if blk == inner_blk:
                    continue
                if state[inner_blk].below is None:
                    actions.append(('(command stack {} {})'.format(blk, inner_blk), step_cost))

    # slide-to command
    # Its preconditions are
    # (1) that both blocks have height 0
    # (2) the second block has fewer than four other blocks side-by-side with it.
    for blk in list(state):
        # Move next to another box
        if state[blk].height == 0:
            for inner_blk in list(state):
                if blk == inner_blk:
                    continue
                if state[inner_blk].height == 0:
                    if blk not in state[inner_blk].side_by_side:
                        if len(state[inner_blk].side_by_side) < 4:
                            actions.append(('(command slide-to {} {})'.format(blk, inner_blk), step_cost))

    return actions


# Function used to apply a command to a specific state.
# The original state is copied and left unmodified.  A copy
# of the modified state will be returned.
def block_world_take_actions(state, command):
    # command is a string of the form '(command action param1 param2)'
    tmp_state = copy.deepcopy(state)
    tmp_command = copy.copy(command[0])
    tmp_command = tmp_command.replace('(', '')
    tmp_command = tmp_command.replace(')', '')
    sub_string = tmp_command.split()
    cmd = sub_string[0].lower()
    action = sub_string[1].lower()
    source = sub_string[2].lower()
    destination = sub_string[3].lower()

    if cmd != 'command':
        print("ERROR: block_world_take_actions - bad command({})".format(command))
        return

    if action == 'slide-to':
        # The preconditions are
        # (1) that both blocks have height 0 and
        # (2) the second block has fewer than four other blocks side-by-side with it.
        # The post-conditions are
        # (1) the first block is side-by-side with the second block
        # (2) the first block is no longer side by side with any block except the second.
        if tmp_state[source].height == 0 and tmp_state[destination].height == 0 and \
           len(tmp_state[destination].side_by_side) < 4:
                # Add first block as neighbor of second block
                tmp_state[destination].side_by_side.append(source)

                # Remove SOURCE block from SOURCEs neighbors
                for blk in tmp_state[source].side_by_side:
                    tmp_state[blk].side_by_side.remove(source)

                # Remove neighbors vertically
                below_src = tmp_state[source].below
                while below_src is not None:
                    # Remove SOURCE block from SOURCEs neighbors
                    for blk in tmp_state[below_src].side_by_side:
                        tmp_state[blk].side_by_side.remove(below_src)
                    tmp_state[below_src].side_by_side.clear()
                    below_src = tmp_state[below_src].below

                # First block is only side-by-side with second block
                tmp_state[source].side_by_side.clear()
                tmp_state[source].side_by_side.append(destination)

                # vertical neighbors
                below_src = tmp_state[source].below
                below_dst = tmp_state[destination].below
                while below_src is not None and below_dst is not None:
                    tmp_state[below_src].side_by_side.append(below_dst)
                    tmp_state[below_dst].side_by_side.append(below_src)
                    below_src = tmp_state[below_src].below
                    below_dst = tmp_state[below_dst].below

    elif action == 'stack':
        # The preconditions
        # (1) neither block has any other block on top of it.
        # The precondition
        # (1) The first block is now on-top-of the second block
        # (2) The first block is no longer on-top-of any other block
        if destination == 'table':
            # Can only move top block
            if tmp_state[source].below is None:
                # If on top of another block, update the lower block
                if tmp_state[source].on_top_of is not None:
                    lower_blk = tmp_state[source].on_top_of
                    tmp_state[lower_blk].below = None

                # If SOURCE block has neighbors, remove SOURCE from neighbors
                for neighbor in tmp_state[source].side_by_side:
                    tmp_state[neighbor].side_by_side.remove(source)

                # SOURCE block is on table and has no neighbors
                tmp_state[source].on_top_of = None
                tmp_state[source].height = 0
                tmp_state[source].side_by_side.clear()

        # stack SOURCE block on top of DESTINATION block
        else:
            # Can only manipulate top blocks
            if tmp_state[source].below is None and tmp_state[destination].below is None:
                # If SOURCE block has neighbors, remove SOURCE from neighbors
                for neighbor in tmp_state[source].side_by_side:
                    tmp_state[neighbor].side_by_side.remove(source)

                # Clear all neighbors from SOURCE
                tmp_state[source].side_by_side.clear()

                # If on top of another block, update the lower block
                if tmp_state[source].on_top_of is not None:
                    lower_blk = tmp_state[source].on_top_of
                    tmp_state[lower_blk].below = None

                # Apply changes for moving block to destination
                tmp_state[source].on_top_of = destination
                tmp_state[source].height = tmp_state[destination].height + 1
                tmp_state[destination].below = source

                # Neighbors of DESTINATION
                for blk in tmp_state[destination].side_by_side:
                    if tmp_state[blk].below is not None:
                        upper_blk = tmp_state[blk].below
                        if len(tmp_state[upper_blk].side_by_side) < 4:
                            tmp_state[source].side_by_side.append(upper_blk)
                            tmp_state[upper_blk].side_by_side.append(source)

    return tmp_state, command[1]

def block_world_heuristic(state, goal):
    height_diff = 0
    neighbor_diff = 0

    # Same blocks must be in both input structures
    for blk in state:
        if state[blk].height != goal[blk].height:
            height_diff += 1
        elif goal[blk].height > 0 and state[blk].on_top_of != goal[blk].on_top_of:
            height_diff += 1

        if goal[blk].height == 0 and state[blk].side_by_side != goal[blk].side_by_side:
            neighbor_diff += 1

    #if neighbor_diff > 0:
    #    neighbor_diff = math.ceil(neighbor_diff / 2.0)

    return height_diff + neighbor_diff


def block_world_heuristic_fast_and_sloppy(state, goal):
    height_diff = 0
    neighbor_diff = 0

    # Same blocks must be in both input structures
    for blk in state:
        if state[blk].height != goal[blk].height:
            height_diff += 1
        elif goal[blk].height > 0 and state[blk].on_top_of != goal[blk].on_top_of:
            height_diff += 1

        if goal[blk].height == 0 and state[blk].side_by_side != goal[blk].side_by_side:
        #if state[blk].side_by_side != goal[blk].side_by_side:
            neighbor_diff += 1

    #if neighbor_diff > 0:
    #    neighbor_diff = math.ceil(neighbor_diff / 2.0)

    neighbor_diff *= 2.5

    return height_diff + neighbor_diff


if __name__ == "__main__":
    print_time = False

    # Local variables to store state data
    initial_state = {}
    goal_state = {}

    # Populate local variables
    setup(initial_state, goal_state)

    # Get current time before A*
    start = time.time()

    if (len(initial_state) < 13):
        h = block_world_heuristic
    else:
        h = block_world_heuristic_fast_and_sloppy
        h = block_world_heuristic

    # Perform the A* search and store the results
    path = aStar.a_star_search(initial_state, block_world_actions, block_world_take_actions,
                               lambda s: block_world_goal_test(s, goal_state),
                               lambda s: h(s, goal_state),
                               return_path=False)

    # Get current time after A* search
    end = time.time()

    # Print results
    for result in path[0]:
        if result is not None:
            print(result[0])

    if print_time:
        print("Processing Time - {}".format(end - start))
