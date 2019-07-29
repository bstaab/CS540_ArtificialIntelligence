from ast import literal_eval as make_tuple
from PathPlanner.Block import Block
import itertools, heapq, copy

class Requirements:
	def __init__(self, start):
		self.groundLocations = set()
		self.wildcards = set()
		self.start = start
		self.blocksList = start.blocks.keys()
		self.relations = set()
		self.relationSets = [set() for _ in range(len(self.blocksList))] #One relationSet for each valid binding
		self.blocks = dict()
		self.finalized = False
		
	def __str__(self):
		if self.finalized:
			return str(self.relationSets[0])
		return str(self.relations)
		
	def fromState(self, state):
		self.relationSets = [copy.deepcopy(state.relations)]
	
	def addRequirement(self, b1, req, b2):
		"""
		Adds a single requirement to the set of requirements that must be satisfied
		
		Args:
			param1: The id of the first block in the requirement
			param2: The name of the requirement, one of: "has", "next-to", "above", or "at"
			param3: The id of the second block in the requirement

		Returns:
			None
		"""
		for b in (b1,b2):
			if "wildcard" in b:
				self.wildcards.add(b)
		if req == "has":
			if b1 not in self.blocks:
				self.blocks[b1] = Block(b1)
				self.blocks[b1].setHeight(0,self.blocks)
			self.relations.add(b1+" "+req+" "+b2[0]+" "+b2[1])
		else:
			if b1 not in self.blocks:
				self.blocks[b1] = Block(b1)
				self.blocks[b1].setHeight(0,self.blocks)
			if type(b2) == tuple:
				self.blocks[b1].setHeight(b2[2],self.blocks)
			else:
				if b2 not in self.blocks:
					self.blocks[b2] = Block(b2)
					self.blocks[b2].setHeight(0,self.blocks)
				if "next-to" in req:
					self.blocks[b1].addAdjacent(b2,self.blocks)
					self.blocks[b2].addAdjacent(b1,self.blocks)
				elif req == "above":
					self.blocks[b1].addAbove(b2,self.blocks)
			self.relations.add(b1+" "+req+" "+str(b2))
		if req == "at":
			self.groundLocations.add((b2[0],b2[1],0))

	def set_highlight_property(self, block_list = []):
		for block in block_list:
			if block not in self.blocks:
				self.blocks[block.id] = Block(block)
			self.blocks[block.id].setProperty('highlight', True)

	def removeInvalidBindings(self, bindings):
		"""
		Takes a list of all potential bindings and removes the invalid ones
		
		Args:
			param1: The list of bindings

		Returns:
			A list of bindings with the invalid ones removed
		"""
		removalList = []
		for i, binding in enumerate(bindings):
			binding = list(binding)
			for r in self.relations:
				if ("has" in r or "at" in r or "above" in r) and "wildcard" in r:
					for b in binding:
						block = b[0]
						wildcard = b[1]
						r = r.replace(wildcard, block)
					if "has" in r and r not in self.start.relations:
						removalList.append(i)
					rs = r.split()
					for rel in self.relations:
						for b in binding:
							block = b[0]
							wildcard = b[1]
							rel = rel.replace(wildcard, block)
						if rs[0]+" "+rs[1] in rel and r != rel:
							removalList.append(i)

		for r in sorted(set(removalList), reverse=True):
			del bindings[r]
		return bindings
			
	def finalize(self):
		"""
		Contains the logic for calculating all of the valid bindings, reduces the bindings to only the 10 closest
		This function should be called after all the requirements have been added

		Returns:
			None
		"""
		bindings = [list(zip(x,self.wildcards)) for x in itertools.permutations(self.blocksList,len(self.wildcards))]
		bindings = self.removeInvalidBindings(bindings)
		self.relationSets = [set() for _ in range(len(bindings))]
		for binding, rs in zip(bindings, self.relationSets):
			binding = list(binding)
			for r in self.relations:
				for b in binding:
					block = b[0]
					wildcard = b[1]
					r = r.replace(wildcard, block)
				rs.add(r)
		self.wildcards = None
		self.blocksList = None
		self.relations = None

		distances = []
		for relations in self.relationSets:
			distances.append((self.calcDistance(relations,self.start),relations))
		self.relationSets = []
		for d, rs in heapq.nsmallest(10,distances,key=lambda x: x[0]):
			self.relationSets.append(rs)
		self.finalized = True
		
	def satisfiesRequirements(self, state):
		"""
		Checks to see if the given state satisfies these requirements
		
		Args:
			param1: The given state

		Returns:
			True if all relations are satisfied; False otherwise 
		"""
		for relations in self.relationSets:
			valid = True
			for r in relations:
				if r not in state.relations:
					valid = False
					break
			if valid is True:
				return True
		return False

	def calcDistance(self, relations, state):
		"""
		Calculates the distance between the given state and the given set of relations
		(This heuristic is a mess and I'm not even sure why it works anymore, but it seems to do fairly well)
		
		Args:
			param1: The given set of relations
			param2: The given state

		Returns:
			An integer representing the estimated number of moves needed 
		"""
		distance = 0
		for r in relations:
			if r not in state.relations:
				rs = r.split()
				if "at" in r:
					b = state.blocks[rs[0]]
					loc = make_tuple(rs[2]+rs[3]+rs[4])
					distance += state.diagonalDistance(b.id, loc[0],loc[1],loc[2]) + 2
					if loc in state.xyzIdx and b.id != state.xyzIdx[loc]:
						distance += 3
					if state.allAdjacent((b.x,b.y,b.z)):
						distance += 2
					new_loc = (b.x,b.y,b.z+1)
					if new_loc in state.xyzIdx and (b.z != 0 or loc[2] != 0):
						distance += 3 + b.z+1
					loc = make_tuple(rs[2]+rs[3]+rs[4])
					if loc[2] > 0:
						for z in range(loc[2]):
							loc = (loc[0],loc[1],z)
							if loc not in state.xyzIdx or state.xyzIdx[loc] == b.id:
								distance += 10
					distance *= 10
				elif "next-to" in r and "nothing" not in r:
					b1 = state.blocks[rs[0]]
					b2 = state.blocks[rs[2]]
					distance += state.diagonalDistance(b1.id,b2.x,b2.y,b2.z) + 2
					new_loc = (b1.x,b1.y,b1.z+1)
					if new_loc in state.xyzIdx and (b1.z != 0 or b2.z != 0):
						distance += 3 + b1.z+1
					if state.allAdjacent((b2.x,b2.y,b2.z)):
						distance += 2
				elif "above" in r and "nothing" not in r:
					b1 = state.blocks[rs[0]]
					if rs[2] == "table":
						distance += b1.z
					else:
						b2 = state.blocks[rs[2]]
						distance += state.diagonalDistance(b1.id,b2.x,b2.y,b2.z+1) + 2
						loc = (b2.x,b2.y,b2.z+1)
						if loc in state.xyzIdx and b1.id != state.xyzIdx[loc]:
							distance += 3 + b2.z+1
						loc = (b1.x,b1.y,b1.z+1)
						if loc in state.xyzIdx:
							distance += 3 + b1.z+1
				elif "above" in r and "nothing" in r:
					b = state.blocks[rs[2]]
					loc = (b.x,b.y,b.z+1)
					while loc in state.xyzIdx:
						distance += 10
						loc = (loc[0],loc[1],loc[2]+1)
					
		return distance

		
	def estimateDistance(self, state):
		"""
		Estimates the smallest distance between the given state and the requirements object
		This function takes into account all of the valid bindings and returns the distance to what it believes is the closest binding
		
		Args:
			param1: The state in question

		Returns:
			An integer representing the estimated number of moves needed 
		"""
		smallest_distance = float('inf')
		for relations in self.relationSets:
			distance = self.calcDistance(relations, state)
			if distance < smallest_distance:
				smallest_distance = distance
		return smallest_distance 
