import block as b
import operator as o
from constants import *


# Helper to determine if two locatioins are adjacent
def is_neighbor(x1, y1, z1, x2, y2, z2):
    return z1 == z2 and ((x1 == x2 and (abs(y1 - y2) == 1)) or (y1 == y2 and (abs(x1 - x2) == 1)))


# Helper function to determine if location 1 is above location 2
def is_above(x1, y1, z1, x2, y2, z2):
    return x1 == x2 and y1 == y2 and z1 == (z2 + 1)


# Helper function to determine if location 1 is below location 2
def is_below(x1, y1, z1, x2, y2, z2):
    return x1 == x2 and y1 == y2 and z2 == (z1 + 1)


# Defines a class to store properties and relations for a single block
class Relation:
    # Function used to initialize object
    def __init__(self, relation_id):
        self.relation_id = relation_id  # relation name
        self.state_data = {}  # The neighbors of this block
        self.grabbed_block = None  # The block_id that is grabbed, None if empty

    # Function to display the contents of the structure when printed
    def __repr__(self):
        return "Relation[" \
               "\trelation_id(" + repr(self.relation_id) + ")" + \
               "\tstate_data(" + repr(self.state_data) + ")" +\
               "\tgrabbed_block(" + repr(self.grabbed_block) + ")]\n"

    # Override object comparison operator '=='
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return o.eq(self.state_data, other.state_data)
        else:
            return False

    # Function to grab a block
    # pre-conditions
    #    - no other block is grabbed
    #    - block is in the relation
    # post-condition
    #    - block is grabbed
    def grab_block(self, block_id):
        if self.grabbed_block is None and block_id in self.state_data:
            self.grabbed_block = block_id
            return True
        else:
            return False

    # Functio to release a block
    # pre-condition
    #    - block is grabbed
    # post-contition
    #    - block is released
    def release_block(self, block_id):
        if self.grabbed_block == block_id:
            self.grabbed_block = None
            return True
        else:
            return False

    # Function to get the grabbed block
    def get_grabbed_block(self):
        return self.grabbed_block

    # Function to all properties (except color) from all blocks in a relation
    def remove_all_block_relationships(self):
        for blk in list(self.state_data):
            self.state_data[blk].remove_all_neighbors()
            self.state_data[blk].set_on_top_of(None)
            self.state_data[blk].set_below(None)

    # Function to find all relationships for blocks in a relation
    def find_all_block_relationships(self):
        for blk in list(self.state_data):
            blk_x, blk_y, blk_z = self.state_data[blk].get_location()
            for inner_blk in list(self.state_data):
                if inner_blk == blk:
                    continue
                if self.state_data[inner_blk].is_location_valid():
                    iblk_x, iblk_y, iblk_z = self.state_data[inner_blk].get_location()
                    if iblk_x == blk_x and iblk_y == blk_y and iblk_z == blk_z:
                        print("ERROR - find_all_block_relationships: 2 blocks at exact same location")
                        exit(1)

                    # If we get here, the blocks do not collide
                    if iblk_z == blk_z:
                        # Same height - check for neighbor
                        if is_neighbor(iblk_x, iblk_y, iblk_z, blk_x, blk_y, blk_z):
                            self.state_data[blk].add_neighbor(inner_blk)
                            self.state_data[inner_blk].add_neighbor(blk)
                    elif iblk_x == blk_x and iblk_y == blk_y:
                        # Same X,Y - check for above or below
                        if iblk_z == (blk_z + 1):
                            # Inner block is above block
                            self.state_data[inner_blk].set_on_top_of(blk)
                            self.state_data[blk].set_below(inner_blk)
                        elif iblk_z == (blk_z - 1):
                            # Inner block is below block
                            self.state_data[blk].set_on_top_of(inner_blk)
                            self.state_data[inner_blk].set_below(blk)
                else:
                    print("ERROR - find_all_block_relationships: inner block location is invalid")

        # After above and below are determined, set heights
        for blk in list(self.state_data):
            blk_height = self.state_data[blk].get_height()
            if blk_height == 0:
                block_above = self.state_data[blk].get_below()
                while block_above is not None:
                    blk_height += 1
                    self.state_data[block_above].set_height(blk_height)
                    block_above = self.state_data[block_above].get_below()

    # Helper function to set [on_top_of, below, neighbors] based on valid location
    def find_relationships_based_on_valid_location(self):
        for blk in list(self.state_data):
            # If blk location is valid, find above and below blocks
            if self.state_data[blk].is_location_valid():
                blk_x, blk_y, blk_z = self.state_data[blk].get_location()
                # Search all blocks in state_data to find above and below blocks
                for inner_blk in list(self.state_data):
                    if blk == inner_blk:
                        continue
                    # Make sure inner block location is valid
                    if self.state_data[inner_blk].is_location_valid():
                        inner_blk_x, inner_blk_y, inner_blk_z = self.state_data[inner_blk].get_location()
                        # Check to see if blk and inner_blk are in the same column
                        if is_above(inner_blk_x, inner_blk_y, inner_blk_z, blk_x, blk_y, blk_z):
                            # inner_blk is setting on blk
                            self.state_data[inner_blk].set_on_top_of(blk)
                            self.state_data[blk].set_below(inner_blk)
                            continue
                        elif is_below(inner_blk_x, inner_blk_y, inner_blk_z, blk_x, blk_y, blk_z):
                            # blk is setting on inner_blk
                            self.state_data[blk].set_on_top_of(inner_blk)
                            self.state_data[inner_blk].set_below(blk)
                            continue
                        elif is_neighbor(inner_blk_x, inner_blk_y, inner_blk_z, blk_x, blk_y, blk_z):
                            self.state_data[blk].add_neighbor(inner_blk)
                            self.state_data[inner_blk].add_neighbor(blk)
                            continue

    def find_above_and_below(self):
        for blk in list(self.state_data):
            on_top_of = self.state_data[blk].get_on_top_of()
            if on_top_of is not None:
                if on_top_of not in self.state_data:
                    # block 'below' does not exist, create it.
                    self.state_data[on_top_of] = b.Block(on_top_of)

                # Set below property for block
                self.state_data[on_top_of].set_below(blk)

                # If current block location is valid, set or verify 'below' block location
                if self.state_data[blk].is_location_valid():
                    # Current block has a valid location
                    blk_x, blk_y, blk_z = self.state_data[blk].get_location()
                    if self.state_data[on_top_of].is_location_valid():
                        # Lower block also has valid location, validate
                        oto_x, oto_y, oto_z = self.state_data[on_top_of].get_location()
                        if blk_x != oto_x or blk_y != oto_y or blk_z != (oto_z + 1):
                            print("ERROR - find_above_and_below: Relation({}) blk location error".format(
                                self.relation_id))
                    else:
                        # Lower block does not have valid data, set it based on current block
                        self.state_data[on_top_of].set_location(blk_x, blk_y, (blk_z - 1))
                else:
                    # Current block does not have valid location, check to see if 'below' block has valid location
                    if self.state_data[on_top_of].is_location_valid():
                        oto_x, oto_y, oto_z = self.state_data[on_top_of].get_location()
                        self.state_data[blk].set_location(oto_x, oto_y, (oto_z + 1))

            # Set neighbors
            for neighbor in self.state_data[blk].get_neighbors():
                if neighbor not in self.state_data:
                    # Neighbor block does not exist, create it
                    self.state_data[neighbor] = b.Block(neighbor)

                # blk has 'neighbor' block listed as neighbor, make sure
                # 'neighbor' block has blk listed as its neighbor as well
                # NOTE: 'add_neighbor' function ensures preconditions are met
                self.state_data[neighbor].add_neighbor(blk)

    def find_vertical_relationships(self):
        # Set neighbors - vertical
        for blk in list(self.state_data):
            blk_neighbors = self.state_data[blk].get_neighbors()
            for neighbor in blk_neighbors:
                # Set neighbors for blocks below the current block
                on_top_of = self.state_data[blk].get_on_top_of()
                if on_top_of is not None:
                    neighbor_on_top_of = self.state_data[neighbor].get_on_top_of()
                    while on_top_of is not None and neighbor_on_top_of is not None:
                        self.state_data[on_top_of].add_neighbor(neighbor_on_top_of)
                        self.state_data[neighbor_on_top_of].add_neighbor(on_top_of)
                        on_top_of = self.state_data[on_top_of].get_on_top_of()
                        neighbor_on_top_of = self.state_data[neighbor_on_top_of].get_on_top_of()

                # Set neighbors for blocks above the current block
                top_block = self.state_data[blk].get_below()
                if top_block is not None:
                    neighbor_top_block = self.state_data[neighbor].get_below()
                    while top_block is not None and neighbor_top_block is not None:
                        self.state_data[top_block].add_neighbor(neighbor_top_block)
                        self.state_data[neighbor_top_block].add_neighbor(top_block)
                        top_block = self.state_data[top_block].get_below()
                        neighbor_top_block = self.state_data[neighbor_top_block].get_below()

    def find_unset_information(self):
        # Try to resolve unset information
        for blk in list(self.state_data):
            found = False
            if not self.state_data[blk].is_location_valid():
                lower_block = self.state_data[blk].get_on_top_of()
                while lower_block:
                    if self.state_data[lower_block].is_location_valid():
                        x, y, z = self.state_data[lower_block].get_location()
                        self.state_data[blk].set_location(x, y, (z + 1))
                        found = True
                        break
                    lower_block = self.state_data[lower_block].get_on_top_of()

                if found:
                    continue

                upper_block = self.state_data[blk].get_below()
                while upper_block:
                    if self.state_data[upper_block].is_location_valid():
                        x, y, z = self.state_data[upper_block].get_location()
                        self.state_data[blk].set_location(x, y, (z - 1))
                        found = True
                        break
                    upper_block = self.state_data[upper_block].get_below()

                if found:
                    continue

    def resolve_wildcards_based_on_single_color(self):
        for blk in list(self.state_data):
            if 'wildcard' in blk.lower():
                blk_color = self.state_data[blk].get_color()
                if blk_color is not None:
                    block = None
                    count = 0
                    for inner_blk in list(self.state_data):
                        if inner_blk == blk:
                            # Skip same block
                            continue

                        if 'wildcard' in inner_blk.lower():
                            # Skip other wildcard blocks
                            continue

                        inner_blk_color = self.state_data[inner_blk].get_color()
                        if inner_blk_color == blk_color:
                            block = inner_blk
                            count += 1

                    # If we found only ONE block with the same color as the wildcard, the wildcard MUST be this block.
                    # Replace all occurence of wildcard with real block name, then remove wildcard
                    if count == 1:
                        if self.state_data[block].is_location_valid():
                            if self.state_data[blk].is_location_valid():
                                # Both locations valid, make sure they match
                                if self.state_data[block].get_location() != self.state_data[blk].get_location():
                                    print("ERROR - RELATION WILDCARD locations do not match")
                                    exit(1)
                        elif self.state_data[blk].is_location_valid():
                            # inner_blk location valid, block location not valid, use inner_blk location
                            x, y, z = self.state_data[blk].get_location()
                            self.state_data[block].set_location(x, y, z)

                        # Set above and below
                        if self.state_data[blk].get_below() is not None:
                            if self.state_data[block].get_below() is not None:
                                # Both set, make sure they are the same
                                if self.state_data[blk].get_below() != self.state_data[block].get_below():
                                    print("ERROR - RELATINO WILDCARD below not match")
                                    exit(1)
                            else:
                                self.state_data[block].set_below(self.state_data[blk].get_below())
                        if self.state_data[blk].get_on_top_of() is not None:
                            if self.state_data[block].get_on_top_of() is not None:
                                # Both set, make sure they are the same
                                if self.state_data[blk].get_on_top_of() != self.state_data[block].get_on_top_of():
                                    print("ERROR - RELATINO WILDCARD on_top_of not match")
                                    exit(1)
                            else:
                                self.state_data[block].get_on_top_of(self.state_data[blk].get_on_top_of())

                        for inner_blk in list(self.state_data):
                            if blk in self.state_data[inner_blk].get_neighbors():
                                self.state_data[inner_blk].remove_neighbor(blk)
                                self.state_data[inner_blk].add_neighbor(block)
                                self.state_data[block].add_neighbor(inner_blk)
                            elif blk == self.state_data[inner_blk].get_on_top_of():
                                self.state_data[inner_blk].set_on_top_of(block)
                            elif blk == self.state_data[inner_blk].get_below():
                                self.state_data[inner_blk].set_below(block)

                        self.state_data.pop(blk, None)
                        continue

    def assign_wildcard_to_block_and_remove(self, wildcard_id, blk_id):
        # Replace all occurence of wildcard with real block name, then remove wildcard
        if self.state_data[wildcard_id].is_location_valid():
            if self.state_data[blk_id].is_location_valid():
                # Both locations valid, make sure they match
                if self.state_data[blk_id].get_location() != self.state_data[wildcard_id].get_location():
                    print("ERROR - RELATION WILDCARD locations do not match")
                    exit(1)
            else:
                # wildcard_id location valid, blk_id location not valid, use wildcard_id location
                x, y, z = self.state_data[wildcard_id].get_location()
                self.state_data[blk_id].set_location(x, y, z)

        # Set below
        if self.state_data[wildcard_id].get_below() is not None:
            if self.state_data[blk_id].get_below() is not None:
                # Both set, make sure they are the same
                if self.state_data[wildcard_id].get_below() != self.state_data[blk_id].get_below():
                    print("ERROR - RELATINO WILDCARD below not match")
                    exit(1)
            else:
                self.state_data[blk_id].set_below(self.state_data[wildcard_id].get_below())

        # Set on_top_of
        if self.state_data[wildcard_id].get_on_top_of() is not None:
            if self.state_data[blk_id].get_on_top_of() is not None:
                # Both set, make sure they are the same
                if self.state_data[wildcard_id].get_on_top_of() != self.state_data[blk_id].get_on_top_of():
                    print("ERROR - RELATINO WILDCARD on_top_of not match")
                    exit(1)
            else:
                self.state_data[blk_id].set_on_top_of(self.state_data[wildcard_id].get_on_top_of())

        for neighbor in self.state_data[wildcard_id].get_neighbors():
            self.state_data[blk_id].add_neighbor(neighbor)

        for inner_blk in list(self.state_data):
            if inner_blk == wildcard_id:
                continue
            if wildcard_id in self.state_data[inner_blk].get_neighbors():
                self.state_data[inner_blk].remove_neighbor(wildcard_id)
                self.state_data[inner_blk].add_neighbor(blk_id)
                self.state_data[blk_id].add_neighbor(inner_blk)
            elif wildcard_id == self.state_data[inner_blk].get_on_top_of():
                self.state_data[inner_blk].set_on_top_of(blk_id)
            elif wildcard_id == self.state_data[inner_blk].get_below():
                self.state_data[inner_blk].set_below(blk_id)

        self.state_data.pop(wildcard_id, None)

    def resolve_wildcards_based_on_defined_attributes(self):
        for blk in list(self.state_data):
            if 'wildcard' in blk.lower():
                # Look for single matching color
                blk_color = self.state_data[blk].get_color()
                if blk_color is not None:
                    block = None
                    count = 0
                    for inner_blk in list(self.state_data):
                        if inner_blk == blk:
                            # Skip same block
                            continue

                        if 'wildcard' in inner_blk.lower():
                            # Skip other wildcard blocks
                            continue

                        inner_blk_color = self.state_data[inner_blk].get_color()
                        if inner_blk_color == blk_color:
                            block = inner_blk
                            count += 1

                    # If we found only ONE block with the same color as the wildcard, the wildcard MUST be this block.
                    # Replace all occurence of wildcard with real block name, then remove wildcard
                    if count == 1:
                        self.assign_wildcard_to_block_and_remove(blk, block)
                        continue

                # Look for single matching 'on_top_of'
                on_top_of = self.state_data[blk].get_on_top_of()
                if on_top_of:
                    count = 0
                    block = None
                    for inner_blk in list(self.state_data):
                        block = inner_blk
                        if inner_blk == blk:
                            # Skip same block
                            continue

                        if 'wildcard' in inner_blk.lower():
                            # Skip other wildcard blocks
                            continue

                        inner_blk_on_top_of = self.state_data[inner_blk].get_on_top_of()
                        if inner_blk_on_top_of == on_top_of:
                            count += 1

                    # If we found only ONE block with the same color as the wildcard, the wildcard MUST be this block.
                    # Replace all occurence of wildcard with real block name, then remove wildcard
                    if count == 1 and block:
                        self.assign_wildcard_to_block_and_remove(blk, block)
                        continue

                # Look for single matching 'below'
                below = self.state_data[blk].get_below()
                if below:
                    count = 0
                    block = None
                    for inner_blk in list(self.state_data):
                        if inner_blk == blk:
                            # Skip same block
                            continue

                        if 'wildcard' in inner_blk.lower():
                            # Skip other wildcard blocks
                            continue

                        inner_blk_below = self.state_data[inner_blk].get_below()
                        if inner_blk_below == below:
                            block = inner_blk
                            count += 1

                    # If we found only ONE block with the same color as the wildcard, the wildcard MUST be this block.
                    # Replace all occurence of wildcard with real block name, then remove wildcard
                    if count == 1 and block:
                        self.assign_wildcard_to_block_and_remove(blk, block)
                        continue

    def resolve_wildcards_from_multiple_colors(self):
        num_wildcards = 0
        num_wildcard_locations = 0
        num_blocks = 0
        num_block_locations = 0
        for blk in list(self.state_data):
            if 'wildcard' in blk.lower():
                num_wildcards += 1
                if self.state_data[blk].is_location_valid():
                    num_wildcard_locations += 1
            else:
                num_blocks += 1
                if self.state_data[blk].is_location_valid():
                    num_block_locations += 1

        num_block_unknown_location = num_blocks - num_block_locations
        if num_block_unknown_location:
            if num_wildcard_locations <= num_block_unknown_location:
                # Try to pick the best fit
                for blk in list(self.state_data):
                    # Find wildcard
                    if 'wildcard' in blk.lower():
                        # If color is set, look for same color block
                        blk_color = self.state_data[blk].get_color()
                        if blk_color:
                            for inner_blk in list(self.state_data):
                                if inner_blk == blk:
                                    continue
                                if 'wildcard' not in inner_blk.lower():
                                    # Make sure colors match
                                    inner_blk_color = self.state_data[inner_blk].get_color()
                                    if blk_color != inner_blk_color:
                                        continue

                                    # Make sure this wildcard not a property of this block
                                    blk_id = self.state_data[blk].get_block_id()
                                    if (blk_id == self.state_data[inner_blk].get_on_top_of() or
                                            blk_id == self.state_data[inner_blk].get_below() or
                                            blk_id in self.state_data[inner_blk].get_neighbors()):
                                        # This wildcard is a property of this block
                                        continue

                                    if self.state_data[blk].is_location_valid():
                                        if self.state_data[inner_blk].is_location_valid():
                                            if self.state_data[blk].get_location() != \
                                                    self.state_data[inner_blk].get_location():
                                                continue

                                    b_oto = self.state_data[blk].get_on_top_of()
                                    i_oto = self.state_data[inner_blk].get_on_top_of()
                                    b_bel = self.state_data[blk].get_below()
                                    i_bel = self.state_data[inner_blk].get_below()

                                    if (b_oto and i_oto and b_oto != i_oto) or (b_bel and i_bel and b_bel != i_bel):
                                        continue

                                    # 'inner_blk' is this wildcard
                                    # Copy properties from tmp_blk to block
                                    self.assign_wildcard_to_block_and_remove(blk, inner_blk)
                                    break

    def resolve_wildcards_based_on_unknown_location(self):
        num_wildcard_locations = 0
        num_block_wo_locations = 0
        for blk in list(self.state_data):
            if 'wildcard' in blk.lower():
                if self.state_data[blk].is_location_valid():
                    num_wildcard_locations += 1
            else:
                if not self.state_data[blk].is_location_valid():
                    num_block_wo_locations += 1

        if num_wildcard_locations and num_block_wo_locations:
            for blk in list(self.state_data):
                if 'wildcard' in blk.lower():
                    if self.state_data[blk].is_location_valid():
                        # Wildcard block location is valid
                        for inner_blk in list(self.state_data):
                            if 'wildcard' not in inner_blk.lower():

                                # Check to see if the locations match
                                if self.state_data[inner_blk].get_location() == self.state_data[blk].get_location():
                                    # Locations match, copy wildcard info to block
                                    self.assign_wildcard_to_block_and_remove(blk, inner_blk)
                                    break

            # If we couldn't find a matching location, look for a different block to assign it to
            for blk in list(self.state_data):
                if 'wildcard' in blk.lower():
                    if self.state_data[blk].is_location_valid():
                        # Wildcard block location is valid
                        for inner_blk in list(self.state_data):
                            if inner_blk == blk:
                                continue

                            if 'wildcard' not in inner_blk.lower():
                                # Check to see if the locations match

                                if not self.state_data[inner_blk].is_location_valid():
                                    # Check to see if we can use this block

                                    # Make sure this wildcard not a property of this block
                                    blk_id = self.state_data[blk].get_block_id()
                                    if (blk_id == self.state_data[inner_blk].get_on_top_of() or
                                            blk_id == self.state_data[inner_blk].get_below() or
                                            blk_id in self.state_data[inner_blk].get_neighbors()):
                                        # This wildcard is a property of this block
                                        continue

                                    b_oto = self.state_data[blk].get_on_top_of()
                                    i_oto = self.state_data[inner_blk].get_on_top_of()
                                    b_bel = self.state_data[blk].get_below()
                                    i_bel = self.state_data[inner_blk].get_below()

                                    if (b_oto and i_oto and b_oto != i_oto) or (b_bel and i_bel and b_bel != i_bel):
                                        continue

                                    # 'inner_blk' is this wildcard
                                    # Copy properties from tmp_blk to block
                                    self.assign_wildcard_to_block_and_remove(blk, inner_blk)
                                    break

    # Just assign wildcards (last ditch effort)
    def resolve_wildcards_remaining_wildcards(self):
        for blk in list(self.state_data):
            if 'wildcard' in blk.lower():
                if self.state_data[blk].is_location_valid():
                    # Wildcard block location is valid
                    for inner_blk in list(self.state_data):
                        if 'wildcard' not in inner_blk.lower():

                            # Check to see if the locations match
                            if self.state_data[inner_blk].get_location() == self.state_data[blk].get_location():
                                # Locations match, copy wildcard info to block
                                self.assign_wildcard_to_block_and_remove(blk, inner_blk)
                                break

    def infer_locations(self):
        # See if we can infer locations
        for blk in list(self.state_data):
            if self.state_data[blk].is_location_valid():
                below_blk = self.state_data[blk].get_below()
                if below_blk:
                    if not self.state_data[below_blk].is_location_valid():
                        x, y, z = self.state_data[blk].get_location()
                        self.state_data[below_blk].set_location(x, y, (z + 1))
                above_blk = self.state_data[blk].get_on_top_of()
                if above_blk:
                    if not self.state_data[above_blk].is_location_valid():
                        x, y, z = self.state_data[blk].get_location()
                        self.state_data[above_blk].set_location(x, y, (z - 1))
            else:
                # Try to get info from above, below and neighbors
                below_blk = self.state_data[blk].get_below()
                if below_blk:
                    if self.state_data[below_blk].is_location_valid():
                        x, y, z = self.state_data[below_blk].get_location()
                        self.state_data[blk].set_location(x, y, (z - 1))
                        continue
                above_blk = self.state_data[blk].get_on_top_of()
                if above_blk:
                    if self.state_data[above_blk].is_location_valid():
                        x, y, z = self.state_data[above_blk].get_location()
                        self.state_data[blk].set_location(x, y, (z + 1))
                        continue

                # Look at neighbors for info
                locations = list()
                for nblk in list(self.state_data[blk].get_neighbors()):
                    if nblk == blk:
                        continue
                    if self.state_data[nblk].is_location_valid():
                        locations.append(self.state_data[nblk].get_location())

                num_locations = len(locations)
                if num_locations == 1:
                    # Pick any space around it
                    for move in adjacent_moves:
                        # Calculate new position (X,Y,Z)
                        new_x = locations[0][0] + move[0]
                        new_y = locations[0][1] + move[1]
                        new_z = locations[0][2]

                        # Skip if move is off the board
                        if not (BOARD_MIN_X <= new_x <= BOARD_MAX_X and BOARD_MIN_Y <= new_y <= BOARD_MAX_Y):
                            continue

                        self.state_data[blk].set_location(new_x, new_y, new_z)
                        break
                elif num_locations > 1:
                    # Figure out later
                    print("ERROR - RELATION num_neighbors")
                    exit(1)

    def infer_locations_neighbors(self):
        # Find all occupied cells on table
        occupied = dict()
        for blk in self.state_data:
            if self.state_data[blk].is_location_valid():
                x, y, z = self.state_data[blk].get_location()
                if not (x, y, z) in occupied:
                    occupied[(x, y, z)] = True

        # See if we can infer locations
        for blk in list(self.state_data):
            if not self.state_data[blk].is_location_valid():
                for neighbor in self.state_data[blk].get_neighbors():
                    if neighbor == blk:
                        continue
                    if self.state_data[neighbor].is_location_valid():
                        nx, ny, nz = self.state_data[neighbor].get_location()

                        # Pick any space around it
                        for move in adjacent_moves:
                            # Calculate new position (X,Y,Z)
                            new_x = nx + move[0]
                            new_y = ny + move[1]
                            new_z = nz

                            # Skip if move is off the board
                            if not (BOARD_MIN_X <= new_x <= BOARD_MAX_X and BOARD_MIN_Y <= new_y <= BOARD_MAX_Y):
                                continue

                            self.state_data[blk].set_location(new_x, new_y, new_z)
                            break

    def look_for_gaps(self):
        # look for gaps in stack
        for blk in list(self.state_data):
            if self.state_data[blk].is_location_valid():
                bx, by, bz = self.state_data[blk].get_location()

                # Block is above the table and has no block below
                # Look for blocks with valid location
                if bz > 0 and self.state_data[blk].get_on_top_of() is None:
                    for stk_blk in list(self.state_data):
                        if stk_blk == blk:
                            continue
                        if self.state_data[stk_blk].is_location_valid():
                            sx, sy, sz = self.state_data[stk_blk].get_location()
                            if sx == bx and sy == by and sz == (bz - 1):
                                self.state_data[stk_blk].set_below(blk)
                                self.state_data[blk].set_on_top_of(stk_blk)
                                break

                # Block is above the table and has no block below
                # Look for blocks with no valid location and use that
                if bz > 0 and self.state_data[blk].get_on_top_of() is None:
                    for stk_blk in list(self.state_data):
                        if stk_blk == blk:
                            continue
                        if not self.state_data[stk_blk].is_location_valid():
                            if ((self.state_data[stk_blk].get_below() is None) and
                                    (self.state_data[stk_blk].get_on_top_of() is None)):
                                # Block with no location info, select this one
                                self.state_data[stk_blk].set_location(bx, by, (bz - 1))
                                self.state_data[stk_blk].set_below(blk)
                                self.state_data[blk].set_on_top_of(stk_blk)
                                break

                # Check to see if something is stacked on top
                # Look for blocks with valid location
                if self.state_data[blk].get_below() is None:
                    for stk_blk in list(self.state_data):
                        if stk_blk == blk:
                            continue
                        if self.state_data[stk_blk].is_location_valid():
                            sx, sy, sz = self.state_data[stk_blk].get_location()
                            if sx == bx and sy == by and sz == (bz + 1):
                                self.state_data[blk].set_below(stk_blk)
                                self.state_data[stk_blk].set_on_top_of(blk)
                                break

    def above_below_position(self):
        # try to set above and below based on position
        for blk in list(self.state_data):
            if self.state_data[blk].is_location_valid():
                bx, by, bz = self.state_data[blk].get_location()

                if bz >= 1 and self.state_data[blk].get_on_top_of() is None:
                    for vblk in list(self.state_data):
                        if vblk == blk:
                            continue
                        if self.state_data[blk].is_location_valid():
                            vx, vy, vz = self.state_data[blk].get_location()
                            if vx == bx and vy == by and vz == (bz - 1):
                                self.state_data[blk].set_on_top_of(vblk)
                                self.state_data[vblk].set_below(blk)
                                break

                if self.state_data[blk].get_below() is None:
                    for vblk in list(self.state_data):
                        if vblk == blk:
                            continue
                        if self.state_data[blk].is_location_valid():
                            vx, vy, vz = self.state_data[vblk].get_location()
                            if vx == bx and vy == by and vz == (bz + 1):
                                self.state_data[vblk].set_on_top_of(blk)
                                self.state_data[blk].set_below(vblk)
                                break

    def guess_1(self):
        for blk in self.state_data:
            if self.state_data[blk].is_location_valid():
                x, y, z = self.state_data[blk].get_location()
                on_top_of = self.state_data[blk].get_on_top_of()
                if z > 0 and on_top_of is None:
                    for inner_blk in self.state_data:
                        if inner_blk == blk:
                            continue
                        if not self.state_data[inner_blk].is_location_valid():
                            below = self.state_data[inner_blk].get_below()
                            if below is None:
                                self.state_data[blk].set_on_top_of(inner_blk)
                                self.state_data[inner_blk].set_below(blk)
                                self.state_data[inner_blk].set_location(x, y, (z - 1))

    def guess(self, other_relation=None):
        if other_relation:
            # Look for invalid locations with initial location on the table
            for blk in self.state_data:
                if not self.state_data[blk].is_location_valid():
                    init_x, init_y, init_z = other_relation.state_data[blk].get_location()
                    collision = False
                    # -----------------------------------
                    # This works for case s6 & 7 - Start
                    if init_z >= 0:
                        # Check to see if the location is free
                        for other_blk in self.state_data:
                            if other_blk == blk:
                                continue
                            if self.state_data[other_blk].is_location_valid():
                                other_blk_x, other_blk_y, other_blk_z = self.state_data[other_blk].get_location()
                                if other_blk_x == init_x and other_blk_y == init_y and other_blk_z == init_z:
                                    collision = True
                                    break

                        if not collision:
                            self.state_data[blk].set_location(init_x, init_y, init_z)
                    # This works for case s6 & 7 - end
                    # -----------------------------------

            # See if we can get state data from neighbor list
            for blk in self.state_data:
                if not self.state_data[blk].is_location_valid():
                    # init_x, init_y, init_z = other_relation.state_data[blk].get_location()

                    for neighbor in self.state_data[blk].get_neighbors():
                        if self.state_data[neighbor].is_location_valid():
                            neighbor_x, neighbor_y, neighbor_z = self.state_data[neighbor].get_location()
                            collision = False
                            for move in adjacent_moves:
                                # Calculate new position (X,Y,Z)
                                new_x = neighbor_x + move[0]
                                new_y = neighbor_y + move[1]
                                new_z = 0

                                # Skip if move is off the board
                                if not (BOARD_MIN_X <= new_x <= BOARD_MAX_X and BOARD_MIN_Y <= new_y <= BOARD_MAX_Y):
                                    continue

                                # Check to see if the location is free
                                for other_blk in self.state_data:
                                    if other_blk == blk:
                                        continue
                                    if self.state_data[other_blk].is_location_valid():
                                        other_blk_x, other_blk_y, other_blk_z = self.state_data[
                                            other_blk].get_location()
                                        # Don't need to check z, assume same X,Y implies tower
                                        if other_blk_x == new_x and other_blk_y == new_y:
                                            collision = True
                                            break
                                        if blk not in self.state_data[other_blk].get_neighbors():
                                            # Make sure new location isn't a neighbor
                                            if (new_x == other_blk_x and abs(new_y - other_blk_y) == 1) or \
                                                    (new_y == other_blk_y and abs(new_x - other_blk_x) == 1):
                                                collision = True
                                                break

                                if not collision:
                                    self.state_data[blk].set_location(new_x, new_y, new_z)
                                    break

                    # Look for invalid location with initial location not on the table
                    if not self.state_data[blk].is_location_valid():
                        # Get location from initial configuration
                        init_x, init_y, init_z = other_relation.state_data[blk].get_location()

                        found = False
                        loop_count = 1
                        while not found:
                            for x_move in all_moves_one_dim:
                                for y_move in all_moves_one_dim:
                                    collision = False

                                    # Calculate new position (X,Y,Z)
                                    # NOTE: loop_count initialized to 1 so we have the chance
                                    #       to move to the ground in one action (X, X, -1)
                                    new_x = init_x + (x_move * loop_count)
                                    new_y = init_y + (y_move * loop_count)
                                    new_z = 0

                                    # Skip if move is off the board
                                    if not (BOARD_MIN_X <= new_x <= BOARD_MAX_X and
                                            BOARD_MIN_Y <= new_y <= BOARD_MAX_Y):
                                        continue

                                    # Check to see if the location is free
                                    for other_blk in self.state_data:
                                        if other_blk == blk:
                                            continue
                                        if self.state_data[other_blk].is_location_valid():
                                            other_blk_x, other_blk_y, other_blk_z = self.state_data[
                                                other_blk].get_location()
                                            # Don't need to check z, assume same X,Y implies tower
                                            if other_blk_x == new_x and other_blk_y == new_y:
                                                collision = True
                                                break
                                            # if blk not in self.state_data[other_blk].get_neighbors():
                                            #    # Make sure new location isn't a neighbor
                                            #    if (new_x == other_blk_x and abs(new_y - other_blk_y) == 1) or \
                                            #            (new_y == other_blk_y and abs(new_x - other_blk_x) == 1):
                                            #        collision = True
                                            #        break

                                    if not collision:
                                        found = True
                                        self.state_data[blk].set_location(new_x, new_y, new_z)
                                        break

                                if found:
                                    break

                            loop_count += 1

    def fix_neighbors(self):
        occupied = dict()
        for blk in self.state_data:
            if self.state_data[blk].is_location_valid():
                x, y, z = self.state_data[blk].get_location()
                if not (x, y, z) in occupied:
                    occupied[(x, y, z)] = True

        # Make sure neighbors are at same height
        for blk in list(self.state_data):
            x, y, z = self.state_data[blk].get_location()

            for neighbor in self.state_data[blk].get_neighbors():
                nx, ny, nz = self.state_data[neighbor].get_location()

                if not is_neighbor(x, y, z, nx, ny, nz):
                    # Drop them to the floor
                    z = 0
                    if not (x, y, z) in occupied:
                        self.state_data[blk].set_location(x, y, z)
                    else:
                        # Find a new spot (assume something close will work)
                        found = False
                        loop_count = 1
                        while not found:
                            for x_move in all_moves_one_dim:
                                for y_move in all_moves_one_dim:
                                    # Calculate new position (X,Y,Z)
                                    # NOTE: loop_count initialized to 1 so we have the chance
                                    #       to move to the ground in one action (X, X, -1)
                                    new_x = x + (x_move * loop_count)
                                    new_y = y + (y_move * loop_count)
                                    new_z = z

                                    # Skip if move is off the board
                                    if not (BOARD_MIN_X <= new_x <= BOARD_MAX_X and
                                            BOARD_MIN_Y <= new_y <= BOARD_MAX_Y):
                                        continue

                                    if not (new_x, new_y, new_z) in occupied:
                                        self.state_data[blk].set_location(new_x, new_y, new_z)
                                        found = True
                                        break

                                if found:
                                    break

                        # Now find a spot for my neighbor
                        x, y, z = self.state_data[blk].get_location()
                        for move in adjacent_moves:
                            # Calculate new position (X,Y,Z)
                            new_x = x + move[0]
                            new_y = y + move[1]
                            new_z = z

                            # Skip if move is off the board
                            if not (BOARD_MIN_X <= new_x <= BOARD_MAX_X and BOARD_MIN_Y <= new_y <= BOARD_MAX_Y):
                                continue

                            if not (new_x, new_y, new_z) in occupied:
                                self.state_data[neighbor].set_location(new_x, new_y, new_z)
                                break

    def floating_blocks(self):
        # Look for floating blocks
        for blk in self.state_data:
            lower_block = False
            table_block = False
            if self.state_data[blk].is_location_valid():
                x, y, z = self.state_data[blk].get_location()
                if z > 0:
                    # Check to see if there is a block below
                    for other_blk in self.state_data:
                        if other_blk == blk:
                            continue
                        if self.state_data[other_blk].is_location_valid():
                            ox, oy, oz = self.state_data[other_blk].get_location()
                            if ox == x and oy == y:
                                if oz == 0:
                                    table_block = True
                                if z - oz == 1:
                                    lower_block = True

                    if not lower_block:
                        if not table_block:
                            # No block below
                            self.state_data[blk].set_location(x, y, 0)
                        else:
                            # lower spot is taken, look for one near by
                            found = False
                            loop_count = 1
                            while not found:
                                for x_move in all_moves_one_dim:
                                    for y_move in all_moves_one_dim:
                                        collision = False

                                        # Calculate new position (X,Y,Z)
                                        # NOTE: loop_count initialized to 1 so we have the chance
                                        #       to move to the ground in one action (X, X, -1)
                                        new_x = x + (x_move * loop_count)
                                        new_y = y + (y_move * loop_count)
                                        new_z = 0

                                        # Skip if move is off the board
                                        if not (BOARD_MIN_X <= new_x <= BOARD_MAX_X and
                                                BOARD_MIN_Y <= new_y <= BOARD_MAX_Y):
                                            continue

                                        # Check to see if the location is free
                                        for other_blk in self.state_data:
                                            if other_blk == blk:
                                                continue
                                            if self.state_data[other_blk].is_location_valid():
                                                other_blk_x, other_blk_y, other_blk_z = self.state_data[
                                                    other_blk].get_location()
                                                # Don't need to check z, assume same X,Y implies tower
                                                if other_blk_x == new_x and other_blk_y == new_y:
                                                    collision = True
                                                    break

                                        if not collision:
                                            found = True
                                            self.state_data[blk].set_location(new_x, new_y, new_z)
                                            break

    # Function to build relationships from a set of data
    def gen_relationships(self, other_relation=None):
        self.find_relationships_based_on_valid_location()
        self.find_above_and_below()
        self.find_vertical_relationships()
        self.find_unset_information()
        self.resolve_wildcards_based_on_defined_attributes()
        self.resolve_wildcards_based_on_single_color()
        self.resolve_wildcards_from_multiple_colors()
        self.resolve_wildcards_based_on_unknown_location()
        self.infer_locations()
        self.infer_locations_neighbors()
        self.find_above_and_below()
        self.look_for_gaps()
        self.above_below_position()

        self.guess_1()
        self.find_relationships_based_on_valid_location()
        self.find_above_and_below()

        self.guess(other_relation)
        self.fix_neighbors()
        self.floating_blocks()
        self.remove_all_block_relationships()   # kind of dangerous
        self.find_all_block_relationships()

    # Function to populate state_data with information in the file
    # in_file: Path to file containing configuration information
    # other_relation: Other relation to help determine current relation
    #                 Typically, this will be the initial state when populating the goal state
    def get_state_from_file(self, in_file, other_relation=None):
        # Read input from file
        with open(in_file) as f:
            raw_state_data = f.readlines()
            for item in raw_state_data:
                # Strip delimiters and break into sub strings
                item = item.replace('(', '')
                item = item.replace(')', '')
                item = item.rstrip()
                sub_string = item.split()
                if len(sub_string) == 0:
                    # Skip empty line
                    continue
                if not 4 <= len(sub_string) <= 6:
                    print("INVALID command - ({})".format(item))
                    continue

                # Index '1' is the block to update/apply information to
                blk = sub_string[1]

                # If the block does not exist, create it with default parameters
                if blk not in self.state_data:
                    self.state_data[blk] = b.Block(blk)

                # Index '0' is the property or relation
                if sub_string[0] == 'has':
                    if sub_string[2] == 'color':
                        if len(sub_string) == 4:
                            self.state_data[blk].set_color(sub_string[3])
                        else:
                            # Expected format is '(has block_id color red)
                            print("INVALID length for 'color' property - ({})".format(item))
                            exit(1)
                    elif sub_string[2] == 'location':
                        if len(sub_string) == 6:
                            # Expected format is '(has block_id location xpos ypos zpos)'
                            self.state_data[blk].set_location(sub_string[3], sub_string[4], sub_string[5])
                        else:
                            print("INVALID length for 'location' property - ({})".format(item))
                            exit(1)
                    else:
                        print("Property NOT supported - ({})".format(item))
                        exit(1)
                elif sub_string[0] == 'is':
                    if len(sub_string) == 4:
                        if sub_string[3] == 'on-top-of':
                            self.state_data[blk].set_on_top_of(sub_string[2])
                        elif sub_string[3] == 'side-by-side':
                            self.state_data[blk].add_neighbor(sub_string[2])
                        else:
                            # relation (sub_string[3]) not supported
                            print("Relation NOT supported - ({})".format(item))
                            continue
                    else:
                        # Expected format is '(has block_id color red)
                        print("INVALID length for relation - ({})".format(item))
                        continue

        # If 'other relation' is provided, make sure they are consistent
        # all blocks exist and the colors are transferred
        if other_relation:
            for blk in other_relation.state_data:
                if blk not in list(self.state_data):
                    # This block is not in this relation
                    # Create it and set the color
                    self.state_data[blk] = b.Block(blk)

            for blk in self.state_data:
                if 'wildcard' in blk.lower():
                    # Skip wildcard, it's only expected to be in goal state
                    continue
                if blk not in other_relation.state_data:
                    print("INVALID Configuration: block({}) not in initial confi relation".format(blk))
                    exit(1)

                if self.state_data[blk].is_color_set():
                    color = self.state_data[blk].get_color()
                    if other_relation.state_data[blk].is_color_set():
                        # Both states have a color for this block, make sure they match
                        other_color = other_relation.state_data[blk].get_color()
                        if other_color != color:
                            print("INVALID Configuration block({}) color {} != {}".format(blk, color, other_color))
                            exit(1)
                    else:
                        # Color not set for this block in other_relation, set it now
                        other_relation.state_data[blk].set_color(color)
                elif other_relation.state_data[blk].is_color_set():
                    # Color is set for this block only in the other relationship
                    # Set it in this relationship (we verified that it wasn't set in the if statement above)
                    other_color = other_relation.state_data[blk].get_color()
                    self.state_data[blk].set_color(other_color)

        # After reading all input data, set implicit relationships for all blocks.
        self.gen_relationships(other_relation)

    def is_valid_state(self):
        is_valid = True

        # Make sure all blocks have a valid location
        for blk in list(self.state_data):
            # Make sure blk location is valid
            if not self.state_data[blk].is_location_valid():
                print("ERROR - is_valid_state: relation({}) is_valid_state: block({}) has invalid location".format(
                    self.relation_id, blk))
                is_valid = False
                # exit(1)

        # Make sure no blocks have the exact same location
        for blk in list(self.state_data):
            blk_x, blk_y, blk_z = self.state_data[blk].get_location()
            # Search all blocks in state_data to find above and below blocks
            for iblk in list(self.state_data):
                if blk == iblk:
                    continue

                # Get inner block data
                iblk_x, iblk_y, iblk_z = self.state_data[iblk].get_location()
                # Check to see if blk and iblk are in the same column
                if iblk_x == blk_x and iblk_y == blk_y and iblk_z == blk_z:
                    print("ERROR - is_valid_state: relation({}) block({}) and block({}) have the same location".format(
                        self.relation_id, blk, iblk))
                    is_valid = False
                    # exit(1)

        # Make sure there are no floating blocks
        for blk in list(self.state_data):
            blk_height = self.state_data[blk].get_height()
            if blk_height > 0:
                on_top_of = self.state_data[blk].get_on_top_of()
                if on_top_of is None:
                    print("ERROR - is_valid_state: relation({}) block({}) height({}) and on_top_of NONE".format(
                        self.relation_id, blk, blk_height))
                    is_valid = False
                    # exit(1)

        # Make sure neighbors are at same height
        for blk in list(self.state_data):
            x, y, z = self.state_data[blk].get_location()

            for neighbor in self.state_data[blk].get_neighbors():
                nx, ny, nz = self.state_data[neighbor].get_location()

                if not is_neighbor(x, y, z, nx, ny, nz):
                    print("ERROR - is_valid_state: neighbor validation blk({}) and blk({})".format(blk, neighbor))
                    is_valid = False
                    # exit(1)

        return is_valid
