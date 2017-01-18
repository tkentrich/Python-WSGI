#!/usr/bin/env python

class Game:
	CREATED = 100
	FILLED = 101
	STARTING = 200
	STARTED = 201
	PAUSED = 202
	COMPLETE = 300

	def __init__(self, creator, scene):
		self.players = [LevelObject(creator)]
		self.objects = [players[-1]]
		self.scene = scene
		# This should depend on the scene
		self.minPlayers = 1
		self.maxPlayers = 2
		self.status = Game.CREATED

	def join(self, joiner):
		if len(self.players) < self.maxPlayers:
			self.players.append(LevelObject(joiner))
			self.addObject(players[-1])
			if len(self.players) == self.maxPlayers:
				self.status = Game.FILLED
		# else Raise('FILLED')

	def start(self):
		if len(self.players) >= self.minPlayers and len(self.players) <= self.maxPlayers and self.status < Game.STARTING:
			i = 0
			for p in self.players:
				# Position should depend on scene
				p.setPosition(0,0,i * 2)
				i += 1

			self.status = Game.STARTING

	def addObject(self, obj):
		self.objects.append(obj)

	def name(self):
		return "%s|%s" % (self.players[0].name, self.scene)

	def desc(self):
		return "%s|%d/%d/%d" % (self.name(), len(self.players), self.minPlayers, self.maxPlayers)

	def getUpdate(self):
		if self.status < Game.STARTED:
			return name() + "^".join([p.name for p in self.players]) 
		elif self.status < Game.COMPLETE:
			return "^".join([p.desc() for p in self.players])

class LevelObject:
	def __init__(self, name):
		self.name = name
		self.setPosition(0,0,0)

	def setPosition(self, x, y, z):
		(self.x, self.y, self.z) = (x, y, z)

	def setPositionVector(self, vectorString):
		[self.x, self.y, self.z] = [float(x) for x in vectorString.split(",")]

	def desc(self):
		return "%s|(%d,%d,%d)" % (self.name, self.x, self.y, self.z)

