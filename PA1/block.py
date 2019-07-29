# Defines a class to store properties and relations for a single block
class Block:
    # Function used to initialize object
    def __init__(self, block_id):
        self.block_id = block_id    # Block name
        self.color = None           # Explicit Parameter
        self.on_top_of = None       # Identifies the block underneath this block, None if 'table'
        self.below = None           # Identifies the block above this block, None if this is the top block
        self.height = 0             # Height of current block, table has height = 0
        self.side_by_side = []      # The neighbors of this block

    # Function to display the contents of the structure when printed
    def __repr__(self):
        return "Block[" \
               "\n\tblock_id(" + repr(self.block_id) + ")" + \
               "\n\tcolor(" + repr(self.color) + ")" + \
               "\n\ton_top_of(" + repr(self.on_top_of) + ")" + \
               "\n\tbelow(" + repr(self.below) + ")" + \
               "\n\theight(" + repr(self.height) + ")" + \
               "\n\tside_by_side(" + repr(self.side_by_side) + ")]"

    # Override object comparison operator '=='
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return  self.block_id       == other.block_id   and \
                    self.height         == other.height     and \
                    self.color          == other.color      and \
                    self.on_top_of      == other.on_top_of  and \
                    self.below          == other.below      and \
                    self.side_by_side   == other.side_by_side
        else:
            return False

    # Function to add a property to the block
    # NOTE: There can only be one value for a property
    def add_property(self, prop_name, prop_value):
        if prop_name.lower() == 'color':
            self.color = prop_value.lower()
        elif prop_name.lower() == 'height':
            self.height = prop_value.lower()
        else:
            print("UNKNOWN property ({})".format(prop_name.lower()))

    # Function to add a relation to the block.
    # The supported relations and their restrictions...
    # on-top-of: A block can only be on top of one box
    # side-by-side: A block can be beside four other blocks (one on each side)
    #               A block can only be beside a box one time
    def add_relation(self, relation_block, relation_value):
        if relation_value.lower() == 'on-top-of':
            self.on_top_of = relation_block.lower()
        elif relation_value.lower() == 'side-by-side':
            # Check to see if 'relation_value' is already in the list
            if not relation_block.lower() in self.side_by_side:
                # 'relation_value' not in list, add if there is room
                if len(self.side_by_side) < 4:
                    self.side_by_side.append(relation_block.lower())

    # Function to remove a relation from the block.
    def remove_relation(self, relation_block, relation_value):
        if relation_value.lower() == 'on-top-of':
            self.on_top_of = None
        elif relation_value.lower() == 'side-by-side':
            # Check to see if 'relation_value' is already in the list
            if relation_value.lower() in self.side_by_side:
                # 'relation_value' in list, add if there is room
                if len(self.side_by_side) < 4:
                    self.side_by_side.pop(relation_block.lower())


# Function to populate state_data with information in the file
# NOTE: This only captures information that was explicitly described in the file
def get_state_from_file(in_file, state_data):
    with open(in_file) as f:
        initial_state_data = f.readlines()
        for item in initial_state_data:
            item = item.replace('(', '')
            item = item.replace(')', '')
            item = item.rstrip()
            sub_string = item.split()
            if len(sub_string) != 4:
                continue

            # Index '1' is the block to update/apply information to
            blk = sub_string[1]

            # If the block does not exist, create it
            if blk not in state_data:
                state_data[blk] = Block(blk)

            # Index '0' is the property or relation
            if sub_string[0] == 'has':
                state_data[blk].add_property(sub_string[2], sub_string[3])
            elif sub_string[0] == 'is':
                state_data[blk].add_relation(sub_string[2], sub_string[3])


# Function to build relationships from a set of data
def gen_relationships(state_data):
    # Make sure there is a block entry for each block described in state_data
    # If one is not present, create a default object.
    for blk in list(state_data):
        if state_data[blk].on_top_of is not None:
            if not state_data[blk].on_top_of in state_data:
                state_data[state_data[blk].on_top_of] = Block(state_data[blk].on_top_of)
            state_data[state_data[blk].on_top_of].below = blk
        for side in state_data[blk].side_by_side:
            if side not in state_data:
                state_data[side] = Block(side)
            if blk not in state_data[side].side_by_side:
                state_data[side].side_by_side.append(blk)

    if True:
        for blk in list(state_data):
            if len(state_data[blk].side_by_side) == 4:
                for neighbor in state_data[blk].side_by_side:
                    if len(state_data[neighbor].side_by_side) == 4:
                        count = 0
                        # This pair should have 2 common neighbors
                        for n1 in state_data[blk].side_by_side:
                            if n1 == neighbor:
                                continue

                            for n1a in state_data[n1].side_by_side:
                                if n1a == blk:
                                    continue
                                for n2a in state_data[neighbor].side_by_side:
                                    if n2a == blk:
                                        continue
                                    if n2a in state_data[n1].side_by_side:
                                        count += 1

                        loop_count = 1
                        while count != 2:
                            blk1 = None
                            blk2 = None
                            for n2 in state_data[blk].side_by_side:
                                if n2 == neighbor:
                                    continue
                                if len(state_data[n2].side_by_side) == loop_count:
                                    blk1 = n2
                                    break
                            for n3 in state_data[neighbor].side_by_side:
                                if n3 == blk:
                                    continue
                                if len(state_data[n3].side_by_side) == loop_count:
                                    blk2 = n3
                                    break

                            if blk1 is None or blk2 is None:
                                loop_count += 1
                            elif blk1 not in state_data[blk2].side_by_side and blk2 not in state_data[blk1].side_by_side:
                               state_data[blk2].side_by_side.append(blk1)
                               state_data[blk1].side_by_side.append(blk2)
                               count += 1

    if True:
        for blk in list(state_data):
            if len(state_data[blk].side_by_side) == 4:
                for neighbor in state_data[blk].side_by_side:
                    if len(state_data[neighbor].side_by_side) == 3:
                        count = 0
                        # This pair should have 2 common neighbors
                        for n1 in state_data[blk].side_by_side:
                            if n1 == neighbor:
                                continue

                            for n1a in state_data[n1].side_by_side:
                                if n1a == blk:
                                    continue
                                for n2a in state_data[neighbor].side_by_side:
                                    if n2a == blk:
                                        continue
                                    if n2a in state_data[n1].side_by_side:
                                        count += 1

                        loop_count = 1
                        while count < 1:
                            blk1 = None
                            blk1_cnt = 4
                            blk2 = None
                            blk2_cnt = 4
                            for n2 in state_data[blk].side_by_side:
                                if n2 == neighbor:
                                    continue
                                if len(state_data[n2].side_by_side) < blk1_cnt:
                                    blk1 = n2
                                    blk1_cnt = len(state_data[n2].side_by_side)
                            for n3 in state_data[neighbor].side_by_side:
                                if n3 == blk:
                                    continue
                                if len(state_data[n3].side_by_side) <= blk2_cnt:
                                    blk2 = n3
                                    blk2_cnt = len(state_data[n3].side_by_side)

                            if blk1 is None or blk2 is None:
                                loop_count += 1
                            elif blk1 not in state_data[blk2].side_by_side and blk2 not in state_data[blk1].side_by_side:
                               state_data[blk2].side_by_side.append(blk1)
                               state_data[blk1].side_by_side.append(blk2)
                               count += 1

    # Set height property for all blocks based on 'on_top_of' property
    for blk in list(state_data):
        if state_data[blk].on_top_of is not None:
            on_top_of = state_data[blk].on_top_of
            while on_top_of is not None:
                state_data[blk].height += 1
                on_top_of = state_data[on_top_of].on_top_of

    # Set below property for all blocks
    for blk in list(state_data):
        if state_data[blk].on_top_of is not None:
            on_top_of = state_data[blk].on_top_of
            state_data[on_top_of].below = blk

    # Set neighbors - reflection
    # If block1 has block2 as a neighbor, make sure
    # block2 has block1 listed as a neighbor
    for blk in list(state_data):
        for neighbor in state_data[blk].side_by_side:
            if blk not in state_data[neighbor].side_by_side:
                if len(state_data[neighbor].side_by_side) < 4:
                    state_data[neighbor].side_by_side.append(blk)
            if state_data[neighbor].height != state_data[blk].height:
                height = max(state_data[neighbor].height, state_data[blk].height)
                state_data[neighbor].height = height
                state_data[blk].height = height

    # Set neighbors - vertical
    for blk in list(state_data):
        for neighbor in state_data[blk].side_by_side:
            # Set neighbors for blocks below the current block
            if state_data[blk].on_top_of is not None:
                on_top_of = state_data[blk].on_top_of
                neighbor_on_top_of = state_data[neighbor].on_top_of
                while on_top_of is not None and neighbor_on_top_of is not None:
                    if neighbor_on_top_of not in state_data[on_top_of].side_by_side:
                        state_data[on_top_of].side_by_side.append(neighbor_on_top_of)
                    if on_top_of not in state_data[neighbor_on_top_of].side_by_side:
                        state_data[neighbor_on_top_of].side_by_side.append(on_top_of)
                    on_top_of = state_data[on_top_of].on_top_of
                    neighbor_on_top_of = state_data[neighbor_on_top_of].on_top_of

            # Set neighbors for blocks above the current block
            if state_data[blk].below is not None:
                top_block = state_data[blk].below
                neighbor_top_block = state_data[neighbor].below
                while top_block is not None and neighbor_top_block is not None:
                    if neighbor_top_block not in state_data[top_block].side_by_side:
                        state_data[top_block].side_by_side.append(neighbor_top_block)
                    if top_block not in state_data[neighbor_top_block].side_by_side:
                        state_data[neighbor_top_block].side_by_side.append(top_block)
                    top_block = state_data[top_block].below
                    neighbor_top_block = state_data[neighbor_top_block].below

    # Assign on_top_of
    break_flag = False
    for blk in list(state_data):
        if state_data[blk].height > 0 and state_data[blk].on_top_of is None:
            # Look for neighbors below that fit the bill
            for neighbor in state_data[blk].side_by_side:
                if state_data[neighbor].on_top_of is not None:
                    tmp = state_data[neighbor].on_top_of
                    for below_neighbor in state_data[tmp].side_by_side:
                        if state_data[below_neighbor].below is None:
                            state_data[below_neighbor].below = blk
                            state_data[blk].on_top_of = below_neighbor
                            break_flag = True
                            break
                    if break_flag == True:
                        break

            if break_flag == False:
                for tmp_blk in list(state_data):
                    if tmp_blk == blk:
                        continue
                    if state_data[tmp_blk].height == state_data[blk].height -1:
                        if state_data[tmp_blk].below is None:
                            if len(state_data[tmp_blk].side_by_side) == 0:
                                state_data[tmp_blk].below = blk
                                state_data[blk].on_top_of = tmp_blk
                                for neighbor in state_data[blk].side_by_side:
                                    foo = state_data[neighbor].on_top_of
                                    if foo is not None:
                                        state_data[foo].side_by_side.append(tmp_blk)
                                        state_data[tmp_blk].side_by_side.append(foo)


if __name__ == "__main__":
    # A dictionary to hold the block information
    blocks = {}
    get_state_from_file("initial_state.txt", blocks)
    gen_relationships(blocks)

    for b in blocks:
        print(blocks[b])
