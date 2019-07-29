
# Function to display all blocks in a 'State'
def show_state(state=None, command=None):
    print("show_state called with command: ", command)
    print("and state: ", state)


def blocksMainThread():
	return False

def present(state=None):
    print("present called with state: ", state)

def stop():
    pass
