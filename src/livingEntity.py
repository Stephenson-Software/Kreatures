 # Copyright (c) 2022 Stephenson Software
 # Apache License 2.0
import random
from flags import Flags
from stats import Stats

# @author Daniel McCoy Stephenson
# @since 2017
class LivingEntity(object):
	def __init__(self, name):
		self.name = name
		self.chanceToFight = random.randint(45, 55)
		self.chanceToBefriend = random.randint(45, 55)
		self.log = ["%s was created." % self.name]
		self.friends = []
		self.stats = Stats()
		self.flags = Flags()
	
	def rollForMovement(self):
		if random.randint(1,10) == 1:
			return True
		else:
			return False
	
	def getNextAction(self, kreature):		
		self.decision = random.randint(0,100)
		if self.decision <= self.chanceToFight: # if fight	
			for i in self.friends:
				if i.name == kreature.name:
					return "nothing" # if creature is a friend, don't fight
			self.stats.numActionsTaken += 1
			return "fight" # if search comes up empty, fight
		elif self.chanceToFight < self.decision: # if befriend
			for i in self.friends:
				if i.name == kreature.name:
					self.stats.numActionsTaken += 1
					return "love" # if creature is a friend, have a baby
			self.stats.numActionsTaken += 1
			return "befriend"
	
	def reproduce(self, kreature):
		self.log.append("%s made a baby with %s!" % (self.name, kreature.name))
		kreature.log.append("%s made a baby with %s!" % (kreature.name, self.name))
		self.stats.numOffspring += 1
		kreature.stats.numOffspring += 1
	
	def fight(self, kreature):
		self.log.append("%s fought and ate %s!" % (self.name, kreature.name))
		kreature.log.append("%s was eaten by %s!" % (kreature.name, self.name))
		self.stats.numCreaturesEaten += 1
		
	def befriend(self, kreature):
		self.log.append("%s made friends with %s!" % (self.name, kreature.name))
		kreature.log.append("%s made friends with %s!" % (kreature.name, self.name))
		self.friends.append(kreature)
		kreature.friends.append(self) # this should hopefully append this creature to kreature's friend list
		self.stats.numFriendshipsForged += 1
		kreature.stats.numFriendshipsForged += 1
	
	def increaseChanceToFight(self):
		self.chanceToFight += self.flags.increaseAmount
		if (self.chanceToFight > 100):
			self.chanceToFight = 100
	
	def decreaseChanceToFight(self):
		self.chanceToFight -= self.flags.increaseAmount
		if (self.chanceToFight < 0):
			self.chanceToFight = 0
	
	def increaseChanceToBefriend(self):
		self.chanceToBefriend += self.flags.increaseAmount
		if (self.chanceToBefriend > 100):
			self.chanceToBefriend = 100
	
	def decreaseChanceToBefriend(self):
		self.chanceToBefriend -= self.flags.increaseAmount
		if (self.chanceToBefriend < 0):
			self.chanceToBefriend = 0