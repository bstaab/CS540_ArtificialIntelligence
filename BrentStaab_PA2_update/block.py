# Defines a class to store properties and relations for a single block
class Block:
    # Function used to initialize object
    def __init__(self, block_id, x_pos=-1, y_pos=-1, z_pos=-1):
        self.block_id = block_id  # Block name
        self.color = None  # Explicit Parameter
        self.on_top_of = None  # Identifies the block underneath this block, None if 'table'
        self.below = None  # Identifies the block above this block, None if this is the top block
        self.side_by_side = []  # The neighbors of this block
        self.x_position = int(x_pos)  # Position of the block on the X axis
        self.y_position = int(y_pos)  # Position of the block on the Y axis
        self.z_position = int(z_pos)  # Position of the block on the Z axis

    # Function to display the contents of the structure when printed
    def __repr__(self):
        return "Block[" \
               "\tblock_id(" + repr(self.block_id) + ")" + \
               "\tcolor(" + repr(self.color) + ")" + \
               "\ton_top_of(" + repr(self.on_top_of) + ")" + \
               "\tbelow(" + repr(self.below) + ")" + \
               "\tside_by_side(" + repr(self.side_by_side) + ")" + \
               "\tPosition(" + repr(self.x_position) + ", " + repr(self.y_position) + ", " + \
               repr(self.z_position) + ")]\n"

    # Override object comparison operator '=='
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.block_id == other.block_id and \
                   self.color == other.color and \
                   self.on_top_of == other.on_top_of and \
                   self.below == other.below and \
                   set(self.side_by_side) == set(other.side_by_side) and \
                   self.x_position == other.x_position and \
                   self.y_position == other.y_position and \
                   self.z_position == other.z_position
        else:
            return False

    def get_block_id(self):
        return self.block_id

    def is_color_set(self):
        return self.color is not None

    # Function to set the 'color' property of a block
    def set_color(self, color):
        self.color = color

    # Function to get the 'color' property of a block
    def get_color(self):
        return self.color

    # Function to set the 'location' property of a block
    def set_location(self, x_pos, y_pos, z_pos):
        if 0 <= int(x_pos) <= 10 and 0 <= int(y_pos) <= 10 and 0 <= int(z_pos):
            self.x_position = int(x_pos)
            self.y_position = int(y_pos)
            self.z_position = int(z_pos)
            return True
        else:
            print("ERROR - Can't set location({}, {}, {})".format(x_pos, y_pos, z_pos))
            return False

    # Function to get the 'location' of a block, returns a tuple of all values
    def get_location(self):
        return int(self.x_position), int(self.y_position), int(self.z_position)

    # Function to determine if the location is valid
    # Must be set (!= -1) and somewhere on the grid 10x10xZ
    def is_location_valid(self):
        return 0 <= int(self.x_position) <= 10 and 0 <= int(self.y_position) <= 10 and 0 <= int(self.z_position)

    # Function to set the 'height' of a block (a.k.a. z-position)
    def set_height(self, height):
        self.z_position = int(height)

    # Function to get the 'height' of a block (a.k.a. z-position)
    def get_height(self):
        return int(self.z_position)

    # Function to set the 'location' property of a block
    # Set to 'None' for on-the-table
    def set_on_top_of(self, block):
        self.on_top_of = block
        return True

    # Function to get the block underneath the current block
    # Returns None if no block beneath (on the table)
    def get_on_top_of(self):
        return self.on_top_of

    # Function to set the block immediately above the current block
    # Set to 'None' if this is the top block
    def set_below(self, block):
        self.below = block
        return True

    # Function to get the block immediately above the current block
    # Returns None if no block above (this is the top block)
    def get_below(self):
        return self.below

    # Function to set the 'location' property of a block
    def add_neighbor(self, block):
        if block not in self.side_by_side:
            if len(self.side_by_side) <= 3:
                self.side_by_side.append(block)
                return True
            else:
                print("ERROR - add_neighbor: Too many neighbors. Can't add neighbor({}) to block({})!".
                      format(block, self.block_id))
                return False

        else:
            # block already in neighbor list
            return False

    # Function to remove a specific neighbor from the list of neighbors
    def remove_neighbor(self, block):
        if block in self.side_by_side:
            self.side_by_side.remove(block)
            return True
        else:
            print("ERROR - block({}) is not in block({}) neighbors!".format(block, self.block_id))
            return False

    # Function to remove ALL neighbors from the list of neighbors
    def remove_all_neighbors(self):
        self.side_by_side.clear()

    # Function to get a list of current neighbors
    def get_neighbors(self):
        return self.side_by_side

    # Function to get the number of neighbors
    def get_num_neighbors(self):
        return len(self.side_by_side)


if __name__ == "__main__":
    # A dictionary to hold the block information
    blocks = {}
    # get_state_from_file("initial_state.txt", blocks)
    # gen_relationships(blocks)

    for b in blocks:
        print(blocks[b])
