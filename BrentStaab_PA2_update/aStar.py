import time


# Maximum amount of time the program can run
# The overall timelimit is 60 minutes (3600 seconds)
# I'm allocating 57.5 minutes (3450 seconds) to ROUTE PLANNER
# and the remaining 5 minutes to the LOW_LEVEL PLANNER
# NOTE: These are total time from start of test
MAX_TIME_IN_SEC_ROUTE_PLANNERR = 3450
MAX_TIME_IN_SEC_LOW_LEVEL = 3600


# A structure used to store A* search data
class Node:
    # Function used to initialize object
    def __init__(self, state, start_time=None, action=None, f=0, g=0, h=0):
        self.state = state              # A specific state in the search space
        self.action = action            # An action used to get to this state
        self.start_time = start_time    # time.time value for start
        self.g = g                      # Cost to get to current state
        self.h = h                      # Heuristic value, estimated cost to goal
        self.f = f                      # Estimated total path cost (f = g + h)

    # Function to display the contents of the structure when printed
    def __repr__(self):
        return "Node[" + \
                "\n\tState " + repr(self.state) + \
                "\n\tAction(" + repr(self.action) + ")" + \
                "\n\tStart Time(" + repr(self.start_time) + ")" + \
                "\n\tg(" + repr(self.g) + ")" + \
                "\n\th(" + repr(self.h) + ")" + \
                "\n\tf(" + repr(self.f) + ")]"


# Defines a function to recursively process a parent node
def a_star_recursive(parent_node, actions_func, take_action_func, goal_test_func, heuristic_func, return_path, f_max):
    timeout = False
    if return_path:
        max_time = MAX_TIME_IN_SEC_ROUTE_PLANNERR
    else:
        max_time = MAX_TIME_IN_SEC_LOW_LEVEL

    if (time.time() - parent_node.start_time) > max_time:
        timeout = True
        # print("****** PROGRAM TIMEOUT ******")

    # Check for goal state
    if goal_test_func(parent_node.state) or timeout:
        if return_path:
            return [parent_node.state], parent_node.g
        else:
            return [parent_node.action], parent_node.state.grabbed_block

    # Get all actions for the current state
    actions = actions_func(parent_node.state)

    # Return if there are no actions for the current state
    if not actions:
        return "failure", float('inf')

    # For each action, apply to current state, determine new path info and store
    children = []
    for action in actions:
        (child_state, step_cost) = take_action_func(parent_node.state, action)
        g = parent_node.g + step_cost
        h = heuristic_func(child_state)
        # f = max(h+g, parent_node.f)
        # NOTE: This seems to work better, not sure why
        f = h + g
        child_node = Node(state=child_state, start_time=parent_node.start_time, action=action, f=f, g=g, h=h)
        children.append(child_node)

    # Process each child state discovered from previous step
    while True:
        # Sort 'children' in ascending order of estimated total path cost (f)
        children.sort(key=lambda n: n.f)

        # Get best child from sorted list
        best_child = children[0]
        if best_child.f > f_max:
            return "failure", best_child.f

        # Get next best child from sorted list
        # Use 'inf' if there is not a next best child
        next_best_child = children[1].f if len(children) > 1 else float('inf')

        # Process the best child and update its estimated total path cost (f) with the result
        result, best_child.f = a_star_recursive(best_child, actions_func, take_action_func, goal_test_func,
                                                heuristic_func, return_path, min(f_max, next_best_child))
        if result is not "failure":
            if return_path:
                result.insert(0, parent_node.state)
            else:
                result.insert(0, parent_node.action)
            return result, best_child.f


# This is the entry point for the A* search.  It bundles the input data in the format
# expected by the recursive a* search function
def a_star_search(start_state, actions_func, take_action_func, goal_test_func,
                  heuristic_func, starting_time, return_path=True):
    h = heuristic_func(start_state)
    start_node = Node(state=start_state, start_time=starting_time, action=None, f=0+h, g=0, h=h)
    return a_star_recursive(start_node,
                            actions_func,
                            take_action_func,
                            goal_test_func,
                            heuristic_func,
                            return_path,
                            float('inf'))
