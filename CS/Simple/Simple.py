#!/usr/bin/env python

class CannotJoin(Exception):
	pass

class Game(object):
	CREATED = 100
	FILLED = 101
	STARTING = 200
	STARTED = 201
	PAUSED = 202
	COMPLETE = 300

	def __init__(self, creator, scene):
		self.players = [Player(creator)]
		self.objects = [self.players[-1]]
		self.scene = scene
		# This should depend on the scene
		self.minPlayers = 1
		self.maxPlayers = 2
		self.status = Game.CREATED

	def join(self, joiner):
		if self.status < Game.FILLED:
			self.players.append(Player(joiner))
			self.addObject(self.players[-1])
			if len(self.players) == self.maxPlayers:
				self.status = Game.FILLED
		else:
			raise CannotJoin(self.status)

	def start(self):
		if len(self.players) >= self.minPlayers and len(self.players) <= self.maxPlayers and self.status < Game.STARTING:
			i = 0
			for p in self.players:
				# Position should depend on scene
				p.setPosition(0,0,i * 2)
				i += 1

			self.status = Game.STARTING

	def startGame(self):
		#Set positions (unless already done...hmm...)
		self.status = Game.STARTED

	def addObject(self, obj):
		self.objects.append(obj)

	def name(self):
		return "%s|%s" % (self.players[0].name, self.scene)

	def desc(self):
		return "%s|%d/%d/%d" % (self.name(), len(self.players), self.minPlayers, self.maxPlayers)

	def getUpdate(self, asker=None):
		if self.status < Game.STARTED:
			if self.status == Game.STARTING and asker != None:
				self.players[asker].notifyStart = True
				allNotified = True
				for p in self.players:
					 if not p.notifyStart:
						allNotified = False
				if allNotified:
					self.startGame()
			return self.name() + "^".join([p.name for p in self.players]) 
		elif self.status < Game.COMPLETE:
			return "^".join([p.desc() for p in self.players])

class LevelObject(object):
	def __init__(self, name):
		self.name = name
		self.setPosition(0,0,0)

	def setPosition(self, x, y, z):
		(self.x, self.y, self.z) = (x, y, z)

	def setPositionVector(self, vectorString):
		[self.x, self.y, self.z] = [float(x) for x in vectorString.split(",")]

	def desc(self):
		return "%s|(%d,%d,%d)" % (self.name, self.x, self.y, self.z)

class Player(LevelObject):
	def __init__(self, name):
		LevelObject.__init__(self, name)
		self.notifiedStart = False
