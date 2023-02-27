 # Copyright (c) 2022 Stephenson Software
 # Apache License 2.0
import random
import time
from world.world import World
from entity.livingEntity import LivingEntity
from config.config import Config

# @author Daniel McCoy Stephenson
class Kreatures:
	def __init__(self):
		self.environment = World()

		self.names = ["Jesse", "Juan", "Jose",
					  "Ralph", "Jeremy", "Bobby",
					  "Johnny", "Douglas", "Peter",
					  "Scott", "Kyle", "Billy",
					  "Terry", "Randy", "Adam"]

		print("What would you like to name your kreature?")
		self.creatureName = input("> ")
		self.playerCreature = LivingEntity(self.creatureName)

		self.running = True
		self.config = Config()
		self.tick = 0

	def initiateEntityActions(self):
		for entity in self.environment.getEntities():
			target = self.environment.getRandomEntity()
			
			if target == entity:
				continue
			
			decision = entity.getNextAction(target)
			
			if decision == "nothing":
				entity.log.append("%s had an argument with %s!" % (entity.name, target.name))
			elif decision == "love":
				entity.reproduce(target)
				entity.increaseChanceToBefriend()
				entity.decreaseChanceToFight()
				self.createEntity()
			elif decision == "fight":
				if (target == self.playerCreature and self.config.godMode):
					continue
				entity.increaseChanceToFight()
				entity.decreaseChanceToBefriend()
				self.environment.removeEntity(target)
				entity.fight(target)
			elif decision == "befriend":
				entity.increaseChanceToBefriend()
				entity.decreaseChanceToFight()
				entity.befriend(target)

	def createEntity(self):
		newEntity = LivingEntity(self.names[random.randint(0,len(self.names) - 1)])
		self.environment.addEntity(newEntity)
	
	def printSummary(self):
		print("=== Summary ===")
		if self.playerCreature.chanceToFight > self.playerCreature.chanceToBefriend:
			print("%s was ferocious." % self.playerCreature.name)
		elif self.playerCreature.chanceToBefriend > self.playerCreature.chanceToFight:
			print("%s was very friendly." % self.playerCreature.name)
		else:
			print("%s was neutral." % self.playerCreature.name)
		print("%s's chance to get into a fight was %d percent." % (self.playerCreature.name, self.playerCreature.chanceToFight))
		print("%s's chance to be nice was %d percent." % (self.playerCreature.name, self.playerCreature.chanceToBefriend))
		print("Kreatures still alive: %d" % self.environment.getNumEntities())
	
	def printStats(self):
		print ("=== Stats ===")
		print("Friendships forged: %d" % self.playerCreature.stats.numFriendshipsForged)
		print("Babies made: %d" % self.playerCreature.stats.numOffspring)
		print("Creatures Eaten: %d" % self.playerCreature.stats.numCreaturesEaten)

	def run(self):
		self.environment.entities[0] = self.playerCreature
		print("")
		
		# code to run a day, then show any new additions to log
		while self.running:
			try:
				print(self.playerCreature.log[0]) # tries to print log entry
				if "eaten" in self.playerCreature.log[0]: # if creature was eaten, break out of loop
					self.running = False
					break
				del self.playerCreature.log[0] # tries to delete log entry
			except: # if list is empty, just keep going
				pass
			
			self.initiateEntityActions()
			time.sleep(self.config.tickLength)
			self.tick += 1
			if (self.tick >= self.config.maxTicks):
				print("Maximum iterations reached.")
				self.running = False
				break

		input("[CONTINUE]")

		self.printSummary()
		self.printStats()


kreatures = Kreatures()
kreatures.run()