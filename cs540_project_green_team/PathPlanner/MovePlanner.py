from PathPlanner.State import State
from PathPlanner.Requirements import Requirements
import sys, copy, heapq, re, time, itertools
from ast import literal_eval as make_tuple

class MovePlanner:
	def __init__(self, backtrace=None):
		self.backtrace = backtrace

	def plan(self, backtrace=None, skipRelease=True):
		"""
		The "driver code" for the move planner
			
		Returns:
			The total number of moves and the number of unique states visited
		"""
		if backtrace is None:
			backtrace = self.backtrace
		moves = []
		unique_states = 0
		for i, (move, goal, start) in enumerate(backtrace):
			bt, states = self.a_star(start, goal, move.split())
			unique_states += states
			#moves += len(bt)
			for j, move in enumerate(bt):
				if skipRelease and i == len(backtrace)-1 and j == len(bt)-1 and "release" in move:
					moves.pop(1)
					continue
				moves.append(move)
		return moves, unique_states
		
	def planMove(self, move, state):
		"""
		Plans the path for a single move in the given state
		
		Args:
			param1: A tuple of strings of the form (block1_id, move, block2_id) where move is one of: "above", "next-to"
					"slide-next-to", "slide-to", or "move-to"
			param2: The current state of the blocks world

		Returns:
			The new state, a list of the string representation of the moves, and the number of unique states visited
		"""
		new_state = copy.deepcopy(state)
		if move[1] == "above":
			d, loc = new_state.placeAbove(move[0],move[2])
			move_str = move[0] + " above "+move[2]+" at "+str(loc)
		elif move[1] == "next-to":
			d, loc = new_state.placeBeside(move[0],move[2])
			move_str = move[0] + " next-to "+move[2]+" at "+str(loc)
		elif move[1] == "slide-next-to":
			d, loc = new_state.slideBeside(move[0],move[2])
			move_str = move[0] + " slide-next-to "+move[2]+" at "+str(loc)
		elif move[1] == "slide-to":
			d, loc = new_state.slideTo(move[0],move[2][0],move[2][1],move[2][2])
			move_str = move[0] + " slide-to " + str(loc)
		elif move[1] == "move-to":
			d, loc = new_state.moveTo(move[0],move[2][0],move[2][1],move[2][2])
			move_str = move[0] + " move-to " + str(loc)
			
		moves, unique_states = self.plan(backtrace=((move_str, new_state, state),), skipRelease=False)
		return new_state, moves, unique_states

	def reconstructBacktrace(self, current, backtrace, block, includeState=False):
		"""
		Constructs the backtrace of the A* algorithm
		
		Args: 
			param1: The current (final) locations
			param2: The dictionary containing the backtrace
			param3: The id of the block being moved
			
		Returns:
			The total number of moves and the number of unique states visited
		"""
		path = []
		while current in backtrace.keys():
			current, move, loc = backtrace[current]
			move_str = ""
			if move[0] == "move":
				move_str = "(command carry "+block+" "+str(move[1][0])+" "+str(move[1][1])+" "+str(move[1][2])+")"
			elif move[0] == "slide":
				move_str = "(command slide "+block+" "+str(move[1][0])+" "+str(move[1][1])+")"
			elif move[0] == "grab":
				move_str = "(command grab "+block+")"
			elif move[0] == "drop":
				move_str = "(command release "+block+")"
			if includeState:
				path.append((move_str, current))
			else:
				path.append((move_str))
		path.reverse()
		return path

	def getValidMoves(self, state, goal, block, move):
		"""
		Gets all the valid moves for the current state
		
		Args: 
			param1: The current state
			param2: The goal for this algorithm
			param3: The id of the block being moved
			param4: The current move that is being planned
			
		Returns:
			A set of valid moves
		"""
		moves = set()
		if state.isGrabbed(block.id):
			moves.add(("drop",))
			diffs = list(itertools.product((-1,0,1),repeat=3))
			for d in diffs:
				loc = (block.x+d[0],block.y+d[1],block.z+d[2])
				if state.spaceIsCarryable(loc[0],loc[1],loc[2],block.id):
					moves.add(("move",d))
		else:
			if state.aboveAvailable(block.id):
				moves.add(("grab",))
			if block.z == 0 and state.roomToSlide(block.id):
				diffs = list(itertools.product((-1,0,1),repeat=2))
				for d in diffs:
					loc = (block.x+d[0],block.y+d[1],0)
					if state.spaceIsCarryable(loc[0],loc[1],loc[2],block.id):
						moves.add(("slide",(d[0],d[1],0)))
		return moves

	def a_star(self, start, goal, relationshipMove):
		"""
		The implementation of the A* algorithm for the move planner
		
		Args: 
			param1: The starting state
			param2: The goal for this algorithm
			param3: The current move that is being planned
			
		Returns:
			The total number of moves and the number of unique states visited
		"""
		frontier = {start}
		settled = set()
		backtrace = {}
		score = {start:0}
		pred_score = []
		block = relationshipMove[0]
		heapq.heappush(pred_score, (score[start]+goal.estimateDistance(start,block),start))
		target = make_tuple(relationshipMove[-3]+relationshipMove[-2]+relationshipMove[-1])
		visited_states = 0
		
		while len(frontier) != 0:
			step, current = heapq.heappop(pred_score)
			
			if current not in frontier:
				continue
				
			if (current.blocks[block].x,current.blocks[block].y,current.blocks[block].z) == target and not current.isGrabbed(block):
				return self.reconstructBacktrace(current, backtrace, block, True), visited_states
				
			frontier.remove(current)
			settled.add(current)
			moves = self.getValidMoves(current, goal, current.blocks[block], relationshipMove)

			for move in moves:
				new_state = copy.deepcopy(current)
				if move[0] == "move":
					b = new_state.blocks[block]
					new_state.setLocation(block,b.x+move[1][0],b.y+move[1][1],b.z+move[1][2],"move")
					loc = move[1]
					d = 2
				elif move[0] == "slide":
					b = new_state.blocks[block]
					new_state.slideTo(block,b.x+move[1][0],b.y+move[1][1],b.z+move[1][2])
					loc = move[1]
					d = 1
				elif move[0] == "grab":
					new_state.grab(block)
					loc = (new_state.blocks[block].x,new_state.blocks[block].y,new_state.blocks[block].z)
					d = 2
				elif move[0] == "drop":
					new_state.drop(block)
					loc = loc = (new_state.blocks[block].x,new_state.blocks[block].y,new_state.blocks[block].z)
					d = 2
					
				if new_state in settled:
					continue
				
				if new_state not in frontier:
					frontier.add(new_state)
				elif move_score >= score[new_state]:
					continue

				move_score = score[current] + d
				visited_states += 1
				backtrace[new_state] = (current, move, loc)
				score[new_state] = move_score
				new_pred_score = move_score+goal.estimateDistance(new_state,block) 
				heapq.heappush(pred_score, (new_pred_score,new_state))
