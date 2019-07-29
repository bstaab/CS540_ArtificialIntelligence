# Defines constraints for the block world
BOARD_MIN_X = 0
BOARD_MAX_X = 10
BOARD_MIN_Y = 0
BOARD_MAX_Y = 10
BOARD_MIN_Z = 0

# Defines all moves, relative to a block, that are adjacent to the current block
adjacent_moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]

# Defines all moves, relative to a block.  This includes adjacet and diagonal.
all_moves = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

# Defines all moves, relative to a block, for one dimension (X or Y)
# Similar to 'all_moves' just an iterative approach
all_moves_one_dim = [1, 0, -1]
