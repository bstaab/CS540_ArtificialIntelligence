import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D


# GRAPH SIZE
GRAPH_MIN = 0
GRAPH_MAX = 10

# Block color definitions
BLOCK_COLOR__EDGE_VALID = "black"
BLOCK_COLOR__FACE_INVALID_COLOR = "pink"
BLOCK_COLOR__EDGE_INVALID_COLOR = "magenta"
BLOCK_COLOR__FACE_NO_COLOR = "white"
BLOCK_COLOR__EDGE_NO_COLOR = "grey"
BLOCK_COLOR__FACE_GRABBED = "yellow"
BLOCK_COLOR__EDGE_GRABBED = "red"
BLOCK_COLOR__FACE_MOVE = "red"
BLOCK_COLOR__EDGE_MOVE = "yellow"
BLOCK_COLOR__FACE_HIGHLIGHT = "white"
BLOCK_COLOR__EDGE_HIGHLIGHT = "red"

# Create object and initial properties
fig = plt.figure(num='CS 540 - Green Team')
ax = fig.gca(projection='3d')
ax.set_xticks(np.arange(GRAPH_MIN, GRAPH_MAX, 1))
ax.set_yticks(np.arange(GRAPH_MIN, GRAPH_MAX, 1))
ax.set_zticks(np.arange(GRAPH_MIN, GRAPH_MAX, 1))

# Variables to hold the block data, face and edge colors
filled = np.zeros((GRAPH_MAX, GRAPH_MAX, GRAPH_MAX))
face_colors = np.empty(filled.shape, dtype=object)
edge_colors = np.empty(filled.shape, dtype=object)

# These are the supported colors by name.
# I couldn't find the definitive list, this came from an online example
color_list = ["red", "green", "blue", "magenta", "yellow", "cyan", "orange", "black", "gray", "sienna", "pink",
              "white", "purple"]


# callback function used to update the active graph
# see 'FuncAnimation', this is called every 'interval' mSec
def animate(i):
    global ax
    global filled
    global face_colors
    global edge_colors

    # Clear old view, this also clears labels and titles
    ax.clear()

    # Set labels and title
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    # ax.set_title('TITLE')

    # Update the graph with global variable content
    ax.voxels(filled, edgecolors=edge_colors, facecolors=face_colors)


# Function to display all blocks in a 'State'
def show_state(state=None, command=None):
    global ax
    global filled
    global face_colors
    global edge_colors
    global color_list

    filled = np.zeros((GRAPH_MAX, GRAPH_MAX, GRAPH_MAX))
    face_colors = np.empty(filled.shape, dtype=object)
    edge_colors = np.empty(filled.shape, dtype=object)

    cmd = None
    id = None

    # Process 'command' if supplied
    if command is not None and type(command) == str:
        # Commands expected to be of the following form
        # (command grab|carry|release|slide block_id)
        if 'slide' in command:
            substr = command.replace('(', '')
            substr = substr.replace(')', '')
            substr = substr.split()

            # Only checking for slide command, grab, release handled below
            if substr[0] == 'command' and substr[1] == 'slide':
                cmd = substr[1]
                id = substr[2]

    if state is not None:
        for key in state.blocks:
            filled[state.blocks[key].x][state.blocks[key].y][state.blocks[key].z] = 1
            if (id is not None) and (id == key or \
                    (state.blocks[key].x == state.blocks[id].x and state.blocks[key].y == state.blocks[id].y)):
                fc = BLOCK_COLOR__FACE_MOVE
                ec = BLOCK_COLOR__EDGE_MOVE
            elif state.blocks[key].grabbed:
                # This block is grabbed, use corresponding colors
                fc = BLOCK_COLOR__FACE_GRABBED
                ec = BLOCK_COLOR__EDGE_GRABBED
            elif 'highlight' in state.blocks[key].properties:
                fc = BLOCK_COLOR__FACE_HIGHLIGHT
                ec = BLOCK_COLOR__EDGE_HIGHLIGHT
            elif 'color' in state.blocks[key].properties:
                # This block has a color property defined
                color_name = state.blocks[key].properties['color']
                if color_name in color_list:
                    # The color is one of the known/supported colors
                    fc = color_name
                    ec = BLOCK_COLOR__EDGE_VALID
                else:
                    # Invalid/unsupported color defined, use corresponding colors
                    fc = BLOCK_COLOR__FACE_INVALID_COLOR
                    ec = BLOCK_COLOR__EDGE_INVALID_COLOR
            else:
                # No color defined, use corresponding colors
                fc = BLOCK_COLOR__FACE_NO_COLOR
                ec = BLOCK_COLOR__EDGE_NO_COLOR

            # Set face and edge colors for this block
            face_colors[state.blocks[key].x][state.blocks[key].y][state.blocks[key].z] = fc
            edge_colors[state.blocks[key].x][state.blocks[key].y][state.blocks[key].z] = ec

def blocksMainThread():
	return True

# Setup graph and display
def present(state=None):
    show_state(state)
    plt.show()


# Close a graph
def stop():
    plt.close()


# Define the callback function and refresh rate (interval) to update (animate) the graph
ani = animation.FuncAnimation(fig, animate, interval=500)


if __name__ == "__main__":
    present()
