from PathPlanner.Block import Block
import copy

class State:
	def __init__(self):
		self.blocks = {}			# key: block ID; value: block
		self.relations = set()
		self.xyzIdx = {}
		
	def __str__(self):
		out = ""
		for b in self.blocks.values():
			out += str(b) + " - "
		return out
		
	def __hash__(self):
		l = []
		for id in sorted(list(self.blocks.keys())):
			block = self.blocks[id]
			l.append(id)
			l.extend(frozenset(block.properties.items()))
			l.append(block.x)
			l.append(block.y)
			l.append(block.z)
			l.append(block.isGrabbed())
		return hash(frozenset(l))
		
	def __lt__(self, other):
		return len(self.relations) < len(other.relations)
		
	def __eq__(self, other):
		return self.relations == other.relations
		
	def add(self, blockid):
		"""
		Adds a new Block to this state. If given a blockid that is already included, it will be ignored
		
		Args:
			param1: The id of the block
			
		Returns:
			None
		"""
		if blockid not in self.blocks:
			self.blocks[blockid] = Block(blockid)
			
	def spaceIsLegal(self, x,y,z,b):
		"""
		Checks whether the given location is a legal space for the block to be moved to
		
		Args:
			param1: The x coordinate of the location
			param2: The y coordinate of the location
			param3: The z coordinate of the location
			param4: The id of the block
			
		Returns:
			A boolean indicating whether the proposed move is legal
		"""
		if (x,y,z) in self.xyzIdx:
			return False
		if z > 0 and (x,y,z-1) not in self.xyzIdx:
			return False
		if z > 0 and (x,y,z-1) in self.xyzIdx and self.xyzIdx[(x,y,z-1)].id == b:
			return False
		if x < 0 or y < 0 or z < 0:
			return False
		if x > 9 or y > 9 or z > 9:
			return False
		return True
		
	def spaceIsCarryable(self, x,y,z,b):
		"""
		Checks whether the given location is a legal space for the block to be carried through
		This is different than IsLegal because the block doesn't need to be placed here, only held temporarily
		
		Args:
			param1: The x coordinate of the location
			param2: The y coordinate of the location
			param3: The z coordinate of the location
			param4: The id of the block
			
		Returns:
			A boolean indicating whether the proposed move is legal
		"""
		if (x,y,z) in self.xyzIdx:
			return False
		if x < 0 or y < 0 or z < 0:
			return False
		if x > 9 or y > 9 or z > 9:
			return False
		return True
		
	def spaceIsOpen(self, x,y,z):
		"""
		Checks whether there is a block in the given location
		
		Args:
			param1: The x coordinate of the location
			param2: The y coordinate of the location
			param3: The z coordinate of the location
			
		Returns:
			A boolean indicating whether the space is empty
		"""
		if (x,y,z) in self.xyzIdx:
			return False
		return True
			
	def setLocation(self, blockid, x, y, z, movement):
		"""
		Sets the x,y, and z coordinate of a block
		Contains all the logic for updating the relations of that block
		The 5th parameter is not used in the logic, but can be useful for debugging
		
		Args:
			param1: The id of the block being set
			param2: The x coordinate of the location
			param3: The y coordinate of the location
			param4: The z coordinate of the location
			param5: A string describing the reason why the block is being moved
			
		Returns:
			None
		"""
		block = self.blocks[blockid]
		self.xyzIdx.pop((block.x, block.y, block.z), None)
		block.setLocation(x,y,z)
		self.xyzIdx[(block.x, block.y, block.z)] = block
		#self.removeBlockRelations(blockid)
		#self.inferBlockRelations(blockid)
		self.inferRelations()
		self.relations.add(blockid+" at "+str((block.x, block.y, block.z)))
		
	def setProperty(self, blockid, prop, val):
		"""
		Sets the property of a specific block
		
		Args:
			param1: The id of the block being set
			param2: The name of the property
			param3: The value that property should be set to
			
		Returns:
			None
		"""
		self.blocks[blockid].setProperty(prop,val)
		self.relations.add(blockid+" has "+prop+" "+val)
		
	def removeBlockRelations(self, b):
		"""
		Removes all the relations containing the given block
		
		Args:
			param1: The id of the block whose relations are being removed
			
		Returns:
			None
		"""
		removedRelations = set()
		for r in self.relations:
			if b in r.split() and "has" not in r and "grabbed" not in r:
				removedRelations.add(r)
		for r in removedRelations:
			self.relations.remove(r)
		
	def inferBlockRelations(self, b):
		"""
		Infers all the relations for the given block
		
		Args:
			param1: The id of the block whose relations are being inferred
			
		Returns:
			None
		"""
		b = self.blocks[b]
		diffs = [(-1,0), (0,-1) , (1,0), (0,1)]
		#If there is a block above us
		if (b.x,b.y,b.z+1) in self.xyzIdx:
			self.relations.add(self.xyzIdx[(b.x,b.y,b.z+1)].id+" above "+b.id)
			self.relations.discard("nothing above "+b.id)
			b.addAbove(self.xyzIdx[(b.x,b.y,b.z+1)].id, self.blocks)
		else:
			self.relations.add("nothing above "+b.id)
			b.above = None
		
		#If there is a block below us
		if (b.x,b.y,b.z-1) in self.xyzIdx:
			self.relations.add(b.id+" above "+self.xyzIdx[(b.x,b.y,b.z-1)].id)
			self.relations.discard("nothing above "+self.xyzIdx[(b.x,b.y,b.z-1)].id)
		
		#If we are on the table
		if b.z == 0:
			self.relations.add(b.id+" above table")
			
		#If there is a block next to us
		for d in diffs:
			if (b.x+d[0],b.y+d[1],b.z) in self.xyzIdx:
				self.relations.add(self.xyzIdx[(b.x+d[0],b.y+d[1],b.z)].id+" next-to "+b.id)
				self.relations.add(b.id+" next-to "+self.xyzIdx[(b.x+d[0],b.y+d[1],b.z)].id)
				if d[0] == 0:
					self.relations.add(self.xyzIdx[(b.x+d[0],b.y+d[1],b.z)].id+" next-to-x "+b.id)
					self.relations.add(b.id+" next-to-x "+self.xyzIdx[(b.x+d[0],b.y+d[1],b.z)].id)
					if (b.x+d[0],b.y+(-1*d[1]),b.z) not in self.xyzIdx: 
						self.relations.add("nothing next-to-x "+b.id)
						self.relations.add(b.id+" next-to-x nothing")
					else:
						self.relations.discard("nothing next-to-x "+b.id)
						self.relations.discard(b.id+" next-to-x nothing")
				if d[1] == 0:
					self.relations.add(self.xyzIdx[(b.x+d[0],b.y+d[1],b.z)].id+" next-to-y "+b.id)
					self.relations.add(b.id+" next-to-y "+self.xyzIdx[(b.x+d[0],b.y+d[1],b.z)].id)
					if (b.x+(-1*d[0]),b.y+d[1],b.z) not in self.xyzIdx: 
						self.relations.add("nothing next-to-y "+b.id)
						self.relations.add(b.id+" next-to-y nothing")
					else:
						self.relations.discard("nothing next-to-y "+b.id)
						self.relations.discard(b.id+" next-to-y nothing")
		
	def inferRelations(self):
		"""
		Infers the relations for all the blocks currently in the state
			
		Returns:
			None
		"""
		for b in self.blocks.keys():
			self.removeBlockRelations(b)
			self.inferBlockRelations(b)
			
	def diagonalDistance(self, b, x, y, z):
		"""
		Calculates the diagonal distance from the given block to the given coordinates
		
		Args:	
			param1: The id of the block in question
			param2: The x coordinate of the location
			param3: The y coordinate of the location
			param4: The z coordinate of the location
			
		Returns:
			None
		"""
		b = self.blocks[b]
		dx = abs(b.x-x)
		dy = abs(b.y-y)
		dz = abs(b.z-z)
		return max(dx,dy,dz)
			
	def makeValid(self):
		"""
		Moves any floating blocks to the ground
			
		Returns:
			None
		"""
		for b in self.blocks.values():
			if b.z > 0 and (b.x,b.y,b.z-1) not in self.xyzIdx:
				for new_z in range(b.z, -1, -1):
					if b.z == 0 or (b.x,b.y,b.z-1) in self.xyzIdx:
						break
				self.moveTo(b.id, b.x, b.y, new_z)
			
	def noneAdjacent(self, loc):
		"""
		Checks whether any blocks are currently (horizontally) adjacent to the given location
		
		Args:
			param1: The location in question in the form (x,y,z)
			
		Returns:
			A boolean indicating whether there are any adjacent blocks
		"""
		if loc in self.xyzIdx:
			return False
		diffs = [(-1,0), (0,-1) , (1,0), (0,1)]
		for d in diffs:
			if (loc[0]+d[0],loc[1]+d[1],loc[2]) in self.xyzIdx:
				return False
		return True
		
	def allAdjacent(self, loc):
		"""
		Checks whether all of the spaces (horizontally) adjacent to the given location contain blocks
		
		Args:
			param1: The location in question in the form (x,y,z)
			
		Returns:
			A boolean indicating whether there are any empty adjacent locations
		"""
		diffs = [(-1,0), (0,-1) , (1,0), (0,1)]
		for d in diffs:
			if (loc[0]+d[0],loc[1]+d[1],loc[2]) not in self.xyzIdx:
				return False
		return True
		
	def roomToSlide(self, b):
		"""
		Checks whether this block can be slid in any direction
		
		Args: 
			param1: The id of the block in question
			
		Returns:
			A boolean indicating whether the block can be slid
		"""
		b = self.blocks[b]
		diffs = [(-1,0), (0,-1) , (1,0), (0,1)]
		for d in diffs:
			if self.spaceIsLegal(b.x+d[0],b.y+d[1],b.z,b.id):
				return True
		return False
		
	def aboveAvailable(self, b):
		"""
		Checks whether there are any blocks above this one
		
		Args: 
			param1: The id of the block in question
			
		Returns:
			A boolean indicating whether there are any blocks above this one
		"""
		b = self.blocks[b]
		return self.spaceIsLegal(b.x,b.y,b.z+1,None)
		
	def besideAvailable(self, b1,b2):
		"""
		Checks whether this block can be carried sideways
		
		Args: 
			param1: The id of the block in question
			
		Returns:
			A boolean indicating whether the block can be carried sideways
		"""
		b1 = self.blocks[b1]
		b2 = self.blocks[b2]
		diffs = [(-1,0), (0,-1) , (1,0), (0,1)]
		for d in diffs:
			available = self.spaceIsLegal(b1.x+d[0],b1.y+d[1],b1.z,b2.id)
			if available:
				return True
		return False
	
	def placeAbove(self, b1, b2, movement="above"):
		"""
		Places a block above another block in the current state
		
		Args: 
			param1: The id of the block being moved
			param2: The id of the block that it is being placed above
			
		Returns:
			The distance that needed to be traversed and the block's new location
		"""
		if b1 not in self.blocks:
			raise AssertionError(b1 +" does not exist")
		if b2 not in self.blocks:
			raise AssertionError(b2 +" does not exist")
		b1 = self.blocks[b1]
		b2 = self.blocks[b2]
		if (b2.x, b2.y, b2.z+1) in self.xyzIdx:
			raise AssertionError("Cannot place "+b1.id+" above "+b2.id+". Space is already taken by "+self.xyzIdx[(b2.x, b2.y, b2.z+1)].id)
		d = self.diagonalDistance(b1.id, b2.x, b2.y, b2.z+1)
		self.setLocation(b1.id, b2.x, b2.y, b2.z+1, movement)
		return d+2, (b2.x, b2.y, b2.z+1)
		
	def placeBeside(self, b1, b2, movement="beside"):
		"""
		Places a block beside another block in the current state
		
		Args: 
			param1: The id of the block being moved
			param2: The id of the block that it is being placed next-to
			
		Returns:
			The distance that needed to be traversed and the block's new location
		"""
		b1 = self.blocks[b1]
		b2 = self.blocks[b2]
		diffs = [(-1,0), (0,-1) , (1,0), (0,1)]
		place = None
		distance = float("inf")
		for d in diffs:
			space = (b2.x+d[0],b2.y+d[1],b2.z)
			if self.spaceIsLegal(space[0],space[1],space[2],b1.id):
				new_distance = self.diagonalDistance(b1.id, space[0], space[1], space[2])
				if distance > new_distance:
					place = copy.deepcopy(space)
					distance = new_distance	
		if place is None:
			raise AssertionError(b1.id+" could not be placed beside "+b2.id+". No available spaces")
		d = self.diagonalDistance(b1.id, place[0], place[1], place[2])
		self.setLocation(b1.id, place[0], place[1], place[2], movement)
		return d+2, (place[0], place[1], place[2])
		
	def slideBeside(self, b1, b2):
		"""
		Slides a block beside another block in the current state
		Different than placeBeside because all blocks above this block are also moved
		
		Args: 
			param1: The id of the block being slid
			param2: The id of the block that it is being slid next-to
			
		Returns:
			The distance that needed to be traversed and the block's new location
		"""
		b1 = self.blocks[b1]
		b2 = self.blocks[b2]
		coords = (b1.x,b1.y,b1.z+1)
		distance, loc = self.placeBeside(b1.id,b2.id,"slide-beside")
		while True:
			if coords in self.xyzIdx:
				newB = self.blocks[self.xyzIdx[coords].id]
				self.placeAbove(newB.id, b1.id,"slide-above")
				b1 = newB
				coords = (coords[0],coords[1],coords[2]+1)
			else:
				break
		return distance-2, loc
		
	def slideTo(self, b, x, y, z):
		"""
		Slides a block to a given location
		Different than moveTo because all blocks above this block are also moved
		
		Args: 
			param1: The id of the block being slid
			param2: The x coordinate in the location
			param3: The y coordinate in the location
			param4: The z coordinate in the location
			
		Returns:
			The distance that needed to be traversed and the block's new location
		"""
		b = self.blocks[b]
		coords = (b.x,b.y,b.z+1)
		distance = self.diagonalDistance(b.id,x,y,z)
		loc = (x,y,z)
		self.setLocation(b.id,x,y,z,"move-to")
		while True:
			if coords in self.xyzIdx:
				newB = self.blocks[self.xyzIdx[coords].id]
				self.placeAbove(newB.id, b.id,"slide-above")
				b = newB
				coords = (coords[0],coords[1],coords[2]+1)
			else:
				break
		return distance, loc
		
	def moveTo(self, b, x, y, z):
		"""
		Carries a block to a given location
		
		Args: 
			param1: The id of the block being slid
			param2: The x coordinate in the location
			param3: The y coordinate in the location
			param4: The z coordinate in the location
			
		Returns:
			The distance that needed to be traversed and the block's new location
		"""
		distance = self.diagonalDistance(b,x,y,z)
		loc = (x,y,z)
		self.setLocation(b,x,y,z,"move-to")
		return distance+2, loc
		
	def grab(self, b):
		"""
		Grabs the specified block
		
		Args: 
			param1: The id of the block being grabbed
			
		Returns:
			None
		"""
		b = self.blocks[b]
		self.relations.add(b.id+" grabbed")
		b.grab()
		
	def drop(self, b):
		"""
		Drops the specified block
		
		Args: 
			param1: The id of the block being grabbed
			
		Returns:
			None
		"""
		b = self.blocks[b]
		self.relations.remove(b.id+" grabbed")
		b.drop()
		
	def isGrabbed(self, b):
		"""
		Checks whether a given block is currently grabbed
		
		Args: 
			param1: The id of the block in question
			
		Returns:
			A boolean indicating whether the block is grabbed
		"""
		if b+" grabbed" in self.relations:
			return True
		return False
				
	def estimateDistance(self, other, b):
		"""
		Estimates the distance between the same block in two different states
		
		Args: 
			param1: The other state
			param2: The id of the block in question
			
		Returns:
			A boolean indicating whether the block is grabbed
		"""
		b = other.blocks[b]
		return self.diagonalDistance(b.id, b.x,b.y,b.z)-1
		
	def satisfiesRequirements(self, other):
		"""
		Determines whether this state is equivalent to another state
		(I think this may be legacy code from PA1, I'd recommend not using it)
		
		Args: 
			param1: The other state
			
		Returns:
			A boolean indicating whether the states are equivalent
		"""
		for bid, b in self.blocks.items():
			if other.blocks[bid].x != b.x or other.blocks[bid].y != b.y or other.blocks[bid].z != b.z or other.blocks[bid].grabbed != b.grabbed:
				return False
		return True
