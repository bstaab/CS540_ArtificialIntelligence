from PathPlanner.State import State
from PathPlanner.Requirements import Requirements
from PathPlanner.MovePlanner import MovePlanner
import sys, copy, heapq, re, time, random
random.seed(5)
from datetime import timedelta

class PathPlanner:
	def __init__(self):
		pass
		
	def initializeStartState(self, filename):
		"""
		Creates the initial state from the given file
			
		Args: 
			param1: The name of the file
				
		Returns:
			A state object representing the provided file
		"""
		state = State()
		with open(filename, "r") as f:
			text = "".join(f.readlines())
			regex = re.compile(".*?\((.*?)\)")
			result = re.findall(regex, text)
		
		result = [x for x in result if x != "\n" and "has" in x]
		for line in result:
			line = line.split()
			state.add(line[1])
			if line[2] == "location":
				state.setLocation(line[1], int(line[3]), int(line[4]), int(line[5]),"init")
			else:
				state.setProperty(line[1], line[2], line[3])
				
		state.inferRelations()
		return state

	def initializeGoalRequirements(self, filename, start):
		"""
		Creates the goal requirements from the given file
			
		Args: 
			param1: The name of the file
				
		Returns:
			A requirements object representing the provided file
		"""
		requirements = Requirements(start)
		with open(filename, "r") as f:
			text = "".join(f.readlines())
			regex = re.compile(".*?\((.*?)\)")
			result = re.findall(regex, text)
		
		result = [x for x in result if x != "\n"]
		for line in result:
			line = line.split()
			if line[3] == "on-top-of":
				requirements.addRequirement(line[1], "above", line[2])
			elif line[3] == "side-by-side":
				requirements.addRequirement(line[1], "next-to", line[2])
			elif line[2] == "location":
				requirements.addRequirement(line[1], "at", (int(line[3]),int(line[4]),int(line[5])))
			else:
				requirements.addRequirement(line[1], "has", (line[2], line[3]))
				
		requirements.finalize()
		return requirements
		
	def writeOutput(self, filename, backtrace):
		"""
		Writes all the moves in a backtrace to a file
			
		Args: 
			param1: The name of the file
			param2: The given backtrace
				
		Returns:
			None
		"""
		with open(filename, "w") as f:
			for move in backtrace:
				f.write(move + "\n")

	def getValidMoves(self, state, goal):
		"""
		Gets all the valid moves for the current state
			
		Args: 
			param1: The current state
			param2: The goal for this algorithm
				
		Returns:
			A set of valid moves
		"""
		moves = set()
		slideable = set()
		moveable = set()
		for bid, b in state.blocks.items():
			if b.z == 0 and state.roomToSlide(b.id):
				slideable.add(bid)
			if state.spaceIsOpen(b.x,b.y,b.z+1):
				moveable.add(bid)
				
		for bid, b in state.blocks.items():	
			for m in moveable:
				if bid != m and state.aboveAvailable(bid):
					moves.add((m,"above",bid))
				if bid != m and state.besideAvailable(bid,m):
					moves.add((m,"next-to",bid))
				for l in goal.groundLocations:
					if l not in state.xyzIdx:
						moves.add((m,"move-to",l))
			for s in slideable:
				if bid != s and state.besideAvailable(bid,s) and b.z == 0:
					moves.add((s,"slide-next-to",bid))
				for l in goal.groundLocations:
					if l not in state.xyzIdx:
						moves.add((s,"slide-to",l))
		return moves
			
	def reconstructBacktrace(self, current, backtrace):
		"""
		Constructs the backtrace of the A* algorithm
			
		Args: 
			param1: The current (final) locations
			param2: The dictionary containing the backtrace
				
		Returns:
			The series of moves discovered by the A* algorithm
		"""
		path = []
		while current in backtrace.keys():
			old_state = copy.deepcopy(current)
			current, move, loc = backtrace[current]
			move_str = ""
			if move[1] == "above":
				move_str = move[0] + " above "+move[2]+" at "+str(loc)
			elif move[1] == "next-to":
				move_str = move[0] + " next-to "+move[2]+" at "+str(loc)
			elif move[1] == "slide-next-to":
				move_str = move[0] + " slide-next-to "+move[2]+" at "+str(loc)
			elif move[1] == "slide-to":
				move_str = move[0] + " slide-to " + str(loc)
			elif move[1] == "move-to":
				move_str = move[0] + " move-to " + str(loc)
			path.append((move_str,old_state,current))
		path.reverse()
		return path
		
	def a_star(self, start, goal):
		"""
		The implementation of the A* algorithm for the move planner
			
		Args: 
			param1: The starting state
			param2: The goal for this algorithm
				
		Returns:
			The series of moves discovered by the A* algorithm
		"""
		frontier = {start}
		settled = set()
		backtrace = {}
		score = {start:0}
		pred_score = []
		heapq.heappush(pred_score, (score[start]+goal.estimateDistance(start),start))
		visited_states = 0
		
		while len(frontier) != 0:
			step, current = heapq.heappop(pred_score)
			
			if current not in frontier:
				continue
				
			if goal.satisfiesRequirements(current):
				return self.reconstructBacktrace(current, backtrace), visited_states, current
				
			frontier.remove(current)
			settled.add(current)
			moves = self.getValidMoves(current, goal)

			for move in moves:
				new_state = copy.deepcopy(current)
				if move[1] == "above":
					d, loc = new_state.placeAbove(move[0],move[2])
				elif move[1] == "next-to":
					d, loc = new_state.placeBeside(move[0],move[2])
				elif move[1] == "slide-next-to":
					d, loc = new_state.slideBeside(move[0],move[2])
				elif move[1] == "slide-to":
					d, loc = new_state.slideTo(move[0],move[2][0],move[2][1],move[2][2])
				elif move[1] == "move-to":
					d, loc = new_state.moveTo(move[0],move[2][0],move[2][1],move[2][2])
					
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
				new_pred_score = move_score+goal.estimateDistance(new_state) 
				heapq.heappush(pred_score, (new_pred_score,new_state))
				
	def planMove(self, move, state):
		"""
		Plans a movement to a single required state
			
		Args: 
			param1: The requested move - a tuple of the form (block1.id, move name, block2.id-or-(x,y,z)). 
					Move name must be one of "next-to", "above", or "at"
			param2: The starting state
				
		Returns:
			The series of moves discovered by the A* algorithm
		"""
		goal = Requirements(state)
		goal.addRequirement(*move)
		goal.finalize()
		backtrace, visited_states, new_state = self.a_star(state, goal)
		movePlanner = MovePlanner(backtrace)
		moves, visited_states = movePlanner.plan(skipRelease=False)
		return new_state, moves, visited_states

if __name__=="__main__":
	#The driving logic for the program. Print statements should be fairly self-documenting
	pp = PathPlanner()
	start_time = time.time()
	print("Initializing starting state and goal requirements...")
	start = pp.initializeStartState(sys.argv[1:][0])
	goal = pp.initializeGoalRequirements(sys.argv[2:][0], start)
	print("Running A*...")
	backtrace, visited_states = pp.a_star(start, goal)
	for move in backtrace:
		print(move[0])
	elapsed = time.time() - start_time
	print("Completed relationship planning in "+str(len(backtrace))+" moves after visiting "+str(visited_states)+" unique states in "+str(timedelta(seconds=elapsed)))
	print()
	start_time = time.time()
	#movePlanner = MovePlanner()
	#moves, visited_states = movePlanner.planMove(("block1", "above", "block2"), start)
	movePlanner = MovePlanner(backtrace)
	moves, visited_states = movePlanner.plan()
	elapsed = time.time() - start_time
	print("Completed move planning in "+str(moves)+" moves after visiting "+str(visited_states)+" unique states in "+str(timedelta(seconds=elapsed)))
