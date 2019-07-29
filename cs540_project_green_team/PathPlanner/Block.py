class Block:
	def __init__(self, id):
		self.id = id
		self.x = -1
		self.y = -1
		self.z = -1
		self.properties = {}
		self.height = -1
		self.above = None
		self.grabbed = False
		self.adj = set()

	def __str__(self):
		return self.id + ": "+str(self.x)+", "+str(self.y)+", "+str(self.z)

	def shortId(self):
		s = self.id
		if s[:5] == "block": s = s[5:]
		return s
	
	def locationStr(self):
		return "%d,%d,%d" % (self.x, self.y, self.z)

	def setLocation(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
		
	def setProperty(self, prop, val):
		self.properties[prop] = val
		
	def grab(self):
		self.grabbed = True
		
	def drop(self):
		self.grabbed = False
	
	def isGrabbed(self):
		return self.grabbed
		
	def setHeight(self, h, blocks):
		"""
		Logic to update the height of this block and
		any blocks adjacent to or above it
		
		Args:
			param1: The new height of the block
			param2: A dictionary containing all the blocks in the current state

		Returns:
			None
		"""
		self.height = h
		if self.above is not None:
			blocks[self.above].setHeight(h+1, blocks)
		for b in self.adj:
			if blocks[b].height < self.height:
				blocks[b].setHeight(h, blocks)
			
	def addAbove(self, bid, blocks):
		"""
		Logic to place a block above this one
		
		Args:
			param1: The ID of the block being placed above
			param2: A dictionary containing all the blocks in the current state

		Returns:
			None
		"""
		self.above = bid
		blocks[self.above].setHeight(self.height+1, blocks)
		
	def addAdjacent(self,bid, blocks):
		"""
		Logic to place a block adjacent to this one
		
		Args:
			param1: The ID of the block being placed above
			param2: A dictionary containing all the blocks in the current state

		Returns:
			None
		"""
		self.adj.add(bid)
		new_height = max(self.height,blocks[bid].height)
		self.setHeight(new_height, blocks)
		blocks[bid].setHeight(new_height, blocks)
