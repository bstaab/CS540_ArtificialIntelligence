import argparse
import copy
import aStar
import relation as r
# import math
import time
from constants import *


# Global flag to determine if the processing time will be
# printed or not.  This functionality is disabled by default.
# Use the '-t' command line option to enable (see the 'setup' function)
print_time_flag = False
print_debug_flag = False
validate_flag = False


# Function to setup/initialize the block world.
# The initial and goal states will be read from a file passed into the script
# ArgumentParser enforces that a value is passed in for each required parameter
# NOTE: I am not explicitly validating that the files exist, downstream file
#       operations will fail if they are not valid
def setup(initial_state_relation, goal_state_relation):
    # Get parameters from command line
    parser = argparse.ArgumentParser(description='CS540: Programming Assignment #2 - NEED TO UPDATE')
    parser.add_argument('-t', '--time', help='Flag to indicate if processing time will be printed or not',
                        action="store_true")
    parser.add_argument('-d', '--debug', help='Flag to enable additional debug messages', action="store_true")
    parser.add_argument('-v', '--validate', help='Flag to enable initial|goal states', action="store_true")
    required_args = parser.add_argument_group('required named arguments')
    required_args.add_argument('-i', '--initial_state', help='Initial state file name', required=True)
    required_args.add_argument('-g', '--goal_state', help='Goal state file name', required=True)

    args = parser.parse_args()

    # Define global variables so this function can update them
    global print_time_flag
    global print_debug_flag
    global validate_flag

    if args.time:
        print_time_flag = True

    if args.debug:
        print_time_flag = True
        print_debug_flag = True

    if args.validate:
        validate_flag = True

    # Initialize the relations with information from command line arguments
    initial_state_relation.get_state_from_file(args.initial_state)
    goal_state_relation.get_state_from_file(args.goal_state, initial_state_relation)


# Function to determine if a given state is the goal state
def block_world_goal_test(state, goal):
    return state == goal


# Function to determine if a given state is the goal state
def route_planner_goal_test(state, goal):
    if state == goal:
        return True

    for blk in state.state_data:
        if state.state_data[blk] == goal.state_data[blk]:
            continue

        if not goal.state_data[blk].is_location_valid():
            if goal.state_data[blk].get_below() != state.state_data[blk].get_below():
                return False
            if goal.state_data[blk].get_on_top_of() != state.state_data[blk].get_on_top_of():
                return False
            if set(goal.state_data[blk].get_neighbors()) != set(state.state_data[blk].get_neighbors()):
                return False
        continue

    # Can't find anything wrong
    return True


# Function to determine all possible moves/commands for a given state.
def route_planner_actions(relation):
    actions = []

    # look for floating blocks
    for blk in list(relation.state_data):
        # Get the current block location
        blk_x, blk_y, blk_z = relation.state_data[blk].get_location()
        if blk_z > 0 and relation.state_data[blk].get_on_top_of() is None:
            # Block is floating, we can only operate on this one for now
            for x_move in all_moves_one_dim:
                for y_move in all_moves_one_dim:
                    for z_move in all_moves_one_dim:
                        occupied = False
                        tmp_x = blk_x + x_move
                        tmp_y = blk_y + y_move
                        tmp_z = blk_z + z_move

                        # Check for move off of board
                        if not (BOARD_MIN_X <= tmp_x <= BOARD_MAX_X and
                                BOARD_MIN_Y <= tmp_y <= BOARD_MAX_Y and tmp_z >= BOARD_MIN_Z):
                            continue

                        # Make sure new space is not occupied
                        for inner_blk in list(relation.state_data):
                            if blk == inner_blk:
                                continue

                            iblk_x, iblk_y, iblk_z = relation.state_data[inner_blk].get_location()
                            if tmp_z == iblk_z and tmp_x == iblk_x and tmp_y == iblk_y:
                                occupied = True
                                break

                        if not occupied:
                            cost = 1
                            actions.append(('(command move {} {} {} {})'.format(blk, tmp_x, tmp_y, tmp_z), cost))

            # Return now
            return actions

    # stack command
    # The preconditions are that either|neither block has a block on top of it
    # Put id1 on top of id2 (command stack block-id1 block-id2).
    # Put id1 on table (command stack block-id1 table).
    for blk in list(relation.state_data):
        # 'stack' only possible for top block (i.e. below == None)
        if relation.state_data[blk].get_below() is None:
            # Get the current block location
            blk_x, blk_y, blk_z = relation.state_data[blk].get_location()

            # Find all other blocks that this one can be stacked on
            for inner_blk in list(relation.state_data):
                if blk == inner_blk:
                    continue
                if relation.state_data[inner_blk].get_below() is None:
                    iblk_x, iblk_y, iblk_z = relation.state_data[inner_blk].get_location()
                    if abs(iblk_x - blk_x) <= 1 and abs(iblk_y - blk_y) <= 1:
                        height_change = abs(iblk_z + 1 - blk_z)
                        # +2 for 'grab' and 'release'
                        # cost = height_change + 2
                        # NOTE: A cost of one seems to work better for some reason?!
                        cost = height_change + 1
                        actions.append(('(command move {} {} {} {})'.format(blk, iblk_x, iblk_y, (iblk_z + 1)), cost))

            # If height > 0, try to stack on table
            # NOTE: This might be too much, maybe just find the first open slot?
            if blk_z > 0:
                found = False
                loop_count = 1
                while not found:
                    for move in all_moves:
                        occupied = False
                        tmp_x = blk_x + (move[0] * loop_count)
                        tmp_y = blk_y + (move[1] * loop_count)
                        tmp_z = blk_z - 1

                        # Check for move off of board
                        if not (BOARD_MIN_X <= tmp_x <= BOARD_MAX_X and BOARD_MIN_Y <= tmp_y <= BOARD_MAX_Y):
                            continue

                        for inner_blk in list(relation.state_data):
                            if blk == inner_blk:
                                continue

                            iblk_x, iblk_y, iblk_z = relation.state_data[inner_blk].get_location()
                            if tmp_z == iblk_z and tmp_x == iblk_x and tmp_y == iblk_y:
                                occupied = True
                                break

                        if not occupied:
                            found = True
                            # cost = blk_z + 2
                            # actions.append(('(command move {} {} {} {})'.format(blk, tmp_x, tmp_y, 0), cost))
                            cost = 1
                            actions.append(('(command move {} {} {} {})'.format(blk, tmp_x, tmp_y, tmp_z), cost))

                    loop_count += 1
                    if loop_count >= 10:
                        print("LOOP COUNT ERROR")
                        exit(1)

    # slide-to command
    # Its preconditions are
    # (1) that both blocks have height 0
    # (2) the second block has fewer than four other blocks side-by-side with it.
    for blk in list(relation.state_data):
        # Get the current block location
        blk_x, blk_y, blk_z = relation.state_data[blk].get_location()

        # Can only slide blocks that are on the table (height = 0)
        if blk_z == 0:
            for move in all_moves:
                occupied = False
                tmp_x = blk_x + move[0]
                tmp_y = blk_y + move[1]

                # Make sure new position is on the board
                if BOARD_MIN_X <= tmp_x <= BOARD_MAX_X and BOARD_MIN_Y <= tmp_y <= BOARD_MAX_Y:
                    # Make sure new position does not collide with any other block
                    for inner_blk in list(relation.state_data):
                        if blk == inner_blk:
                            continue

                        iblk_x, iblk_y, iblk_z = relation.state_data[inner_blk].get_location()
                        if tmp_x == iblk_x and tmp_y == iblk_y:
                            occupied = True
                            break

                    if not occupied:
                        actions.append(('(command move {} {} {} {})'.format(blk, tmp_x, tmp_y, 0), 1))

    return actions


# Function used to apply a command to a specific state.
# The original state is copied and left unmodified.  A copy
# of the modified state will be returned.
def route_planner_take_actions(relation, command):
    # command is a string of the form '(command move blk x, y, z)'
    tmp_relation = copy.deepcopy(relation)
    tmp_command = copy.copy(command[0])
    tmp_command = tmp_command.replace('(', '')
    tmp_command = tmp_command.replace(')', '')
    sub_string = tmp_command.split()
    cmd = sub_string[0].lower()
    action = sub_string[1].lower()
    block = sub_string[2].lower()

    if cmd != 'command':
        print("ERROR: block_world_take_actions - bad command({})".format(command))
        return

    if action == 'move':
        # Get current location
        blk_x, blk_y, blk_z = tmp_relation.state_data[block].get_location()

        # Get new locations
        new_x = int(sub_string[3])
        new_y = int(sub_string[4])
        new_z = int(sub_string[5])

        # Check for slide or stack moves
        if blk_z == new_z == 0:
            # SLIDE - old and new location is on the table
            upper_block = tmp_relation.state_data[block].get_below()
            while upper_block is not None:
                # Set new X,Y location for blocks in this stack
                ub_height = tmp_relation.state_data[upper_block].get_height()
                tmp_relation.state_data[upper_block].set_location(new_x, new_y, ub_height)
                upper_block = tmp_relation.state_data[upper_block].get_below()

            # Set new X,Y location for this block
            tmp_relation.state_data[block].set_location(new_x, new_y, new_z)
        else:
            # STACK - old and/or new location is not on the table
            # Can only move the top block
            if tmp_relation.state_data[block].get_below() is not None:
                print("route_planner_take_actions - stack error: not top block")
                exit(1)

            # If we're moving the top block, update the block below
            below_block = tmp_relation.state_data[block].get_on_top_of()
            if below_block is not None:
                tmp_relation.state_data[below_block].set_below(None)

            tmp_relation.state_data[block].set_on_top_of(None)
            if new_z == 0:
                tmp_relation.state_data[block].set_on_top_of(None)
            else:
                # Find the top block of the stack this is going on
                for inner_blk in list(tmp_relation.state_data):
                    if inner_blk == block:
                        continue

                    iblk_x, iblk_y, iblk_z = tmp_relation.state_data[inner_blk].get_location()
                    if (iblk_x == new_x) and (iblk_y == new_y):
                        top_block = inner_blk
                        test_block = tmp_relation.state_data[top_block].get_below()
                        while test_block is not None:
                            top_block = test_block
                            test_block = tmp_relation.state_data[top_block].get_below()

                        tmp_relation.state_data[top_block].set_below(block)
                        tmp_relation.state_data[block].set_on_top_of(top_block)
                        break

            # Set new location
            tmp_relation.state_data[block].set_location(new_x, new_y, new_z)
    else:
        print("ERROR - UNKNOWN action({})".format(command[0]))
        exit(1)

    # If we get here, we must have moved a piece.  Rather than try to surgically update the neighbors,
    # remove them all and regenerate for the new configuration.
    for blk in list(tmp_relation.state_data):
        tmp_relation.state_data[blk].remove_all_neighbors()

    for blk in list(tmp_relation.state_data):
        blk_x, blk_y, blk_z = tmp_relation.state_data[blk].get_location()
        for inner_blk in list(tmp_relation.state_data):
            if inner_blk == blk:
                continue
            if tmp_relation.state_data[inner_blk].is_location_valid():
                iblk_x, iblk_y, iblk_z = tmp_relation.state_data[inner_blk].get_location()
                if iblk_x == blk_x and iblk_y == blk_y and iblk_z == blk_z:
                    print("ERROR - find_all_neighbors: 2 blocks at exact same location")
                    exit(1)

                if iblk_z == blk_z and \
                        ((iblk_x == blk_x and (abs(iblk_y - blk_y) == 1)) or
                         (iblk_y == blk_y and (abs(iblk_x - blk_x) == 1))):
                    tmp_relation.state_data[blk].add_neighbor(inner_blk)
                    tmp_relation.state_data[inner_blk].add_neighbor(blk)
            else:
                print("ERROR - find_all_neighbors: inner block location is invalid")

    return tmp_relation, command[1]


# Function used to estimate the remaining steps from state to goal
def route_planner_heuristic(state, goal):
    diff = 0
    for blk in state.state_data:
        # Check to see if block in it's goal state
        if state.state_data[blk] == goal.state_data[blk]:
            continue

        # Get block location from state data
        sblk_x, sblk_y, sblk_z = state.state_data[blk].get_location()

        # Next step based on goal block being set
        if goal.state_data[blk].is_location_valid():
            gblk_x, gblk_y, gblk_z = goal.state_data[blk].get_location()

            # Check for block on table
            if sblk_z == 0:
                # Block is on the table, add street distance to destination
                diff += abs(gblk_x - sblk_x) + abs(gblk_y - sblk_y) + abs(gblk_z - sblk_z)
                # diff += max(abs(gblk_x - sblk_x), abs(gblk_y - sblk_y), abs(gblk_z - sblk_z))
            else:
                # Block is on another block.
                # Find the bottom block, then get the distance from it's goal to block goal
                block = blk
                lower_block = state.state_data[blk].get_on_top_of()
                while lower_block is not None:
                    block = lower_block
                    lower_block = state.state_data[block].get_on_top_of()

                lblk_sx, lblk_sy, lblk_sz = state.state_data[block].get_location()
                lblk_gx, lblk_gy, lblk_gz = goal.state_data[block].get_location()
                if block == blk or (lblk_gx == lblk_sx and lblk_gy == lblk_sy):
                    diff += abs(gblk_x - sblk_x) + abs(gblk_y - sblk_y) + abs(gblk_z - sblk_z)
                    # diff += max(abs(gblk_x - sblk_x), abs(gblk_y - sblk_y), abs(gblk_z - sblk_z))
                else:
                    diff += abs(gblk_x - lblk_gx) + abs(gblk_y - lblk_gy) + abs(gblk_z - lblk_gz)
                    # diff += max(abs(gblk_x - lblk_gx), abs(gblk_y - lblk_gy), abs(gblk_z - lblk_gz))
        else:
            # Destination is not set
            top_block = goal.state_data[blk].get_on_top_of()
            if top_block:
                if goal.state_data[top_block].is_location_valid():
                    gx, gy, gz = goal.state_data[top_block].get_location()
                    gz -= 1  # Subtract 1 since we're below this box
                    diff += abs(gx - sblk_x) + abs(gy - sblk_y) + abs(gz - sblk_z)
                    continue

            bottom_block = goal.state_data[blk].get_on_top_of()
            if bottom_block:
                if goal.state_data[bottom_block].is_location_valid():
                    gx, gy, gz = goal.state_data[top_block].get_location()
                    gz += 1  # Add 1 since we're above this box
                    diff += abs(gx - sblk_x) + abs(gy - sblk_y) + abs(gz - sblk_z)
                    continue

            neighbors = goal.state_data[blk].get_neighbors()
            if neighbors:
                occupied = dict()
                for neighbor in neighbors:
                    if goal.state_data[neighbor].is_location_valid():
                        gx, gy, gz = goal.state_data[neighbor].get_location()
                        if not (gx, gy, gz) in occupied:
                            occupied[(gx, gy, gz)] = True

                # If we have at least one valid location, look for neighbor
                # NOTE: This can be improved if we have more than one neighbor
                if len(occupied):
                    adjacent_moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    for move in adjacent_moves:
                        new_x = sblk_x + move[0]
                        new_y = sblk_y + move[1]
                        new_z = sblk_z

                        # Skip if move is off the board
                        if not (0 <= new_x <= 10 and 0 <= new_y <= 10):
                            continue

                        if not (new_x, new_y, new_z) in occupied:
                            diff += abs(new_x - sblk_x) + abs(new_y - sblk_y) + abs(new_z - sblk_z)
                            continue

                # If we get here, we haven't been able to find anything out
                # Since two blocks need to be side by side, lets use the distance between
                # NOTE: this can be improved if we have more than one neighbor to find the better one
                occupied = dict()
                for inner_blk in goal.state_data:
                    if goal.state_data[inner_blk].is_location_valid():
                        ix, iy, iz = goal.state_data[inner_blk].get_location()
                        if not (ix, iy, iz) in occupied:
                            occupied[(ix, iy, iz)] = True

                # Let's just put them on the table
                for move in all_moves:
                    new_x = sblk_x + move[0]
                    new_y = sblk_y + move[1]
                    new_z = 0

                    # Skip if move is off the board
                    if not (0 <= new_x <= 10 and 0 <= new_y <= 10):
                        continue

                    if not (new_x, new_y, new_z) in occupied:
                        occupied[(new_x, new_y, new_z)] = True
                        # Found this block location, now find neigbor
                        for a_move in all_moves:
                            new_2x = new_x + a_move[0]
                            new_2y = new_y + a_move[1]
                            new_2z = 0

                            # Skip if move is off the board
                            if not (0 <= new_2x <= 10 and 0 <= new_2y <= 10):
                                continue

                            if not (new_2x, new_2y, new_2z) in occupied:
                                diff += abs(new_x - new_2x) + abs(new_y - new_2y) + abs(new_z - new_2z)
                                break

    return diff


# Function to determine all possible moves/commands for a given state.
def block_world_actions(relation):
    actions = []

    grbd_block = relation.get_grabbed_block()

    for blk in list(relation.state_data):
        blk_x, blk_y, blk_z = relation.state_data[blk].get_location()

        for x_move in all_moves_one_dim:
            for y_move in all_moves_one_dim:
                for z_move in all_moves_one_dim:

                    # Check for no change
                    if x_move == 0 and y_move == 0 and z_move == 0:
                        continue

                    # Calculate new position (X,Y,Z)
                    new_x = blk_x + x_move
                    new_y = blk_y + y_move
                    new_z = blk_z + z_move

                    # Check for move off of board
                    if not (BOARD_MIN_X <= new_x <= BOARD_MAX_X and
                            BOARD_MIN_Y <= new_y <= BOARD_MAX_Y and new_z >= 0):
                        continue

                    # Initialize variables
                    slide = blk_z == 0 and new_z == 0
                    stack = False
                    table = relation.state_data[blk].get_below() is None

                    # Check the new position against all other blocks for collision and stack
                    for inner_blk in list(relation.state_data):
                        if inner_blk == blk:
                            continue

                        # Get inner block's location
                        iblk_x, iblk_y, iblk_z = relation.state_data[inner_blk].get_location()

                        # Check for slide collision, exact same X,Y
                        # Don't care about Z because we assume a stack has block(s) under it
                        if iblk_x == new_x and iblk_y == new_y:
                            # Same X, Y means slide collision
                            slide = False
                            table = False

                            if iblk_z == new_z:
                                # Same X, Y and Z
                                stack = False
                                break

                            # Same X, Y AND inner_blk immediately below means we can stack
                            if iblk_z == (new_z - 1) and relation.state_data[blk].get_below() is None:
                                stack = True

                        # If we found a slide collision AND a valid stack, no need to look further
                        # Else keep checking because another block may change the overall result

                        # bstaab - debugging
                        # if not slide and stack:
                        #     break

                    # If no block is grabbed, potential moves are:
                    # - slide
                    # - grab + carry
                    if grbd_block is None:
                        if slide:
                            actions.append([('(command slide {} {} {})'.format(blk, x_move, y_move), 1)])

                        if stack or table:
                            action = []
                            if grbd_block is None:
                                action.append(('(command grab {})'.format(blk), 1))

                            action.append(('(command carry {} {} {} {})'.format(blk, x_move, y_move, z_move), 1))
                            actions.append(action)

                    # If the current block is grabbed, the only move is
                    # - carry
                    elif grbd_block == blk:
                        if stack or table:
                            actions.append([('(command carry {} {} {} {})'.format(blk, x_move, y_move, z_move), 1)])

                    # Someother block is grabbed, the potential moves are
                    # - release_old + slide_new
                    # - release_old + grab_new + carry_new
                    else:
                        if slide:
                            action = list()
                            action.append(('(command release {})'.format(grbd_block), 1))
                            action.append(('(command slide {} {} {})'.format(blk, x_move, y_move), 1))
                            actions.append(action)

                        if stack or table:
                            action = list()
                            action.append(('(command release {})'.format(grbd_block), 1))
                            action.append(('(command grab {})'.format(blk), 1))
                            action.append(('(command carry {} {} {} {})'.format(blk, x_move, y_move, z_move), 1))
                            actions.append(action)

    return actions


# Function used to apply a command to a specific state.
# The original state is copied and left unmodified.  A copy
# of the modified state will be returned.
def block_world_take_actions(relation, actions):
    # Make a copy of the relation
    tmp_relation = copy.deepcopy(relation)
    cost = 0
    update_relation = False

    for command in actions:
        # command is a string of the form '(command action param1 param2)'
        tmp_command = copy.copy(command[0])
        tmp_command = tmp_command.replace('(', '')
        tmp_command = tmp_command.replace(')', '')
        sub_string = tmp_command.split()
        if len(sub_string) < 3:
            print("ERROR")
        cmd = sub_string[0].lower()
        action = sub_string[1].lower()
        source = sub_string[2].lower()

        if cmd != 'command':
            print("ERROR: block_world_take_actions - bad command({})".format(command))
            return

        if action == 'grab':
            # (command grab block-id)
            # The pre-conditions are
            # 1) No block is on top of this block, this is the top block
            # 2) No other block is grabbed
            # The post-condition
            # 1) block-id is grabbed
            cost += 1
            grbd_block = tmp_relation.get_grabbed_block()
            if grbd_block is not None:
                print("ERROR: Can't grab block({}), block({}) already grabbed".format(source, grbd_block))
                exit(1)

            source = sub_string[2].lower()
            if source not in tmp_relation.state_data:
                print("ERROR: grab block({}) NOT in relation".format(source))
                exit(1)

            top_block = tmp_relation.state_data[source].get_below()
            if top_block is not None:
                print("ERROR: grab block({}) NOT the top block, is below({})".format(source, top_block))
                exit(1)

            tmp_relation.grab_block(source)
            continue

        elif action == 'release':
            # (command release block-id)
            # The pre-conditions are
            # 1) Block-id is currently grabbed
            # The post-condition
            # that it is no longer grabbed
            cost += 1
            if source != tmp_relation.get_grabbed_block():
                print("ERROR: release block({}) NOT grabbed".format(source))
                exit(1)

            tmp_relation.release_block(source)
            continue

        elif action == 'slide':
            # (command slide block-id deltaX deltaY)
            # The pre-conditions are
            # 1) The new location is unoccupied (Not going to verify...to expensive)
            # 2) The block has height 0
            # 3) No block currently grabbed
            # The post-conditions are
            # 1) The location of block-id is (x+deltax, y+deltay, z)
            # 2) The blocks with the same initial X,Y are also incrementd
            #     i.e. if blocks are stacked, the whole stack slides
            cost += 1
            update_relation = True
            grbd_block = tmp_relation.get_grabbed_block()
            if grbd_block is not None:
                print("ERROR: Can't SLIDE because block({}) is grabbed".format(grbd_block))
                exit(1)

            height = tmp_relation.state_data[source].get_height()
            if height != 0:
                print("ERROR: Can't SLIDE because block({}) height({}) != 0".format(grbd_block, height))
                exit(1)

            blk_x, blk_y, blk_z = tmp_relation.state_data[source].get_location()
            new_x = blk_x + int(sub_string[3])
            new_y = blk_y + int(sub_string[4])
            tmp_relation.state_data[source].set_location(new_x, new_y, blk_z)

            top_block = tmp_relation.state_data[source].get_below()
            while top_block is not None:
                tblk_x, tblk_y, tblk_z = tmp_relation.state_data[top_block].get_location()
                if tblk_x != blk_x or tblk_y != blk_y:
                    print("ERROR - SLIDE on_top_block XY != current block XY")
                    exit(1)

                tmp_relation.state_data[top_block].set_location(new_x, new_y, tblk_z)
                top_block = tmp_relation.state_data[top_block].get_below()

        elif action == 'carry':
            # (command carry block-id deltaX deltaY deltaZ)
            # The pre-conditions
            # 1) block-id is currently grabbed
            # 1) The destination location is empty (Not going to verify...to expensive)
            # The post-conditions
            # 1) block-id is now at (x+deltaX, y+deltaY, z+deltaZ)
            cost += 1
            update_relation = True
            if tmp_relation.get_grabbed_block() != source:
                print("ERROR - CARRY: block({}) not grabbed".format(source))
                exit(1)

            blk_x, blk_y, blk_z = tmp_relation.state_data[source].get_location()
            new_x = blk_x + int(sub_string[3])
            new_y = blk_y + int(sub_string[4])
            new_z = blk_z + int(sub_string[5])
            tmp_relation.state_data[source].set_location(new_x, new_y, new_z)

    if update_relation:
        tmp_relation.remove_all_block_relationships()
        tmp_relation.find_all_block_relationships()

    return tmp_relation, cost


# Function used to estimate the remaining steps from state to goal
# NOTE: This function calculates the number of incorrect blocks
#       and assumes they can reach the correct state in one step
def block_world_heuristic(state, goal):
    dist_diff = 0
    neighbor_diff = 0

    # Same blocks must be in both input structures
    for blk in state.state_data:
        if state.state_data[blk].get_on_top_of() != goal.state_data[blk].get_on_top_of():
            neighbor_diff += 1

        if state.state_data[blk].get_neighbors() != goal.state_data[blk].get_neighbors():
            neighbor_diff += 1

        sblk_x, sblk_y, sblk_z = state.state_data[blk].get_location()
        gblk_x, gblk_y, gblk_z = goal.state_data[blk].get_location()
        dist_diff += abs(gblk_x - sblk_x) + abs(gblk_y - sblk_y) + abs(gblk_z - sblk_z)

    return dist_diff + neighbor_diff


if __name__ == "__main__":
    # Local variables to store state data
    initial_state = r.Relation('initial_state')
    goal_state = r.Relation('goal_state')

    # Populate local variables
    setup(initial_state, goal_state)

    # Conditionally print debug information
    if print_debug_flag:
        print("-------- INITIAL STATE --------")
        print(initial_state)
        print("\n\n-------- GOAL STATE --------")
        print(goal_state)

    # Verify initial and goal states if flag indicates to do so
    if validate_flag:
        # Verify initial state
        if not initial_state.is_valid_state():
            exit(1)

        # Verify goal state
        if not goal_state.is_valid_state():
            exit(1)

    # Get current time before A*
    start_time = time.time()

    # Conditionally print debug information
    if print_debug_flag:
        print("\n\n-------------------------------")
        print("Runing Route Planner")

    # Route planner - Perform the A* search and store the results
    path = aStar.a_star_search(initial_state,
                               route_planner_actions,
                               route_planner_take_actions,
                               # lambda s: route_planner_goal_test(s, goal_state),
                               lambda s: block_world_goal_test(s, goal_state),
                               lambda s: route_planner_heuristic(s, goal_state),
                               start_time,
                               return_path=True)

    # Conditionally print debug information
    if print_debug_flag:
        route_planner_time = time.time()
        print("Route Planner Finished - steps({}) time({})".format(len(path[0]), (route_planner_time - start_time)))
        for p in path[0]:
            print(p)
        print("-------------------------------")
        print("\n\nRunning Low Level Search")

    # This is the lower level search
    lpath = list()
    num_steps = len(path[0])
    grabbed_block = path[0][0].grabbed_block
    for i in range(0, num_steps - 1, 1):
        # Level 2 planner - Perform the A* search and store the results
        path[0][i].grabbed_block = grabbed_block
        ipath = aStar.a_star_search(path[0][i],
                                    block_world_actions,
                                    block_world_take_actions,
                                    lambda s: block_world_goal_test(s, path[0][i+1]),
                                    lambda s: block_world_heuristic(s, path[0][i+1]),
                                    start_time,
                                    return_path=False)
        lpath.append(ipath)
        grabbed_block = ipath[1]

    # Get current time after low-level search
    end_time = time.time()

    # Conditionally print debug information
    if print_debug_flag:
        print("Low Level search finished")
        for lp in lpath:
            print(lp)
        print("-------------------------------")
        print("\nPATH")

    # ALWAYS print low level commands
    for step_path in lpath:
        for steps in step_path[0]:
            if type(steps) is list:
                for step in steps:
                    print(step[0])

    # Conditionally print total processing time
    if print_time_flag:
        print("Processing Time - {}".format(end_time - start_time))
