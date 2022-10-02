 # Copyright (c) 2022 Stephenson Software
 # Apache License 2.0
from entity import Entity
import random
import time

# @author Daniel McCoy Stephenson
# @since 2017
class Simulation(object):
	
	def __init__(self):
				
		# create ten creatures for the world to have to start with
		self.Alison = Entity("Alison")
		self.Barry = Entity("Barry")
		self.Conrad = Entity("Conrad")
		self.Derrick = Entity("Derrick")
		self.Eric = Entity("Eric")
		self.Francis = Entity("Francis")
		self.Gary = Entity("Gary")
		self.Harry = Entity("Harry")
		self.Isabelle = Entity("Isabelle")
		self.Jasper = Entity("Jasper")
		
		self.listOfKreatures = ["placeholder", self.Alison, self.Barry, self.Conrad, self.Derrick, self.Eric,
						    self.Francis, self.Gary, self.Harry, self.Isabelle, self.Jasper]
						    
		self.listOfRandomNames = ["Jesse", "Juan", "Jose", "Ralph", "Jeremy", "Bobby", "Johnny", "Douglas", "Peter", "Scott", "Kyle", "Billy", "Terry", "Randy", "Adam"]

		self.running = True

	def run(self):
		print("What would you like to name your kreature?")
		
		self.creatureName = input("> ")
		self.playerCreature = Entity(self.creatureName)
		self.listOfKreatures[0] = self.playerCreature
		
		print("")
		
		# code to run a day, then show any new additions to log
		while self.running:
			try:
				print(self.playerCreature.log[0]) # tries to print log entry
				
				if "eaten" in self.playerCreature.log[0]: # if creature was eaten, break out of loop
					break
				
				del self.playerCreature.log[0] # tries to delete log entry
			
			except: # if list is empty, just keep going
				pass
			
			self.initiateEntityActions()
			
			time.sleep(1)
			
		if self.playerCreature.chanceToFight > self.playerCreature.chanceToBefriend:
			print("%s was ferocious." % self.playerCreature.name)
		
		elif self.playerCreature.chanceToBefriend > self.playerCreature.chanceToFight:
			print("%s was very friendly." % self.playerCreature.name)
		
		input("[CONTINUE]")
		print("Friendships forged: %d" % self.playerCreature.friendsMade)
		print("Babies made: %d" % self.playerCreature.babiesMade)
		print("Creatures Eaten: %d" % self.playerCreature.creaturesEaten)
		print("%s's chance to get into a fight was %d percent." % (self.playerCreature.name, self.playerCreature.chanceToFight))
		print("%s's chance to be nice was %d percent." % (self.playerCreature.name, self.playerCreature.chanceToBefriend))
		print("Kreatures still alive: %d" % len(self.listOfKreatures))	
				
	def initiateEntityActions(self):
		for i in self.listOfKreatures:
			self.who = self.listOfKreatures[random.randint(0,len(self.listOfKreatures) - 1)]
			
			if self.who == i:
				continue
			
			self.decision = i.getNextAction(self.who)
			
			if self.decision == "nothing":
				i.log.append("%s had an argument with %s!" % (i.name, self.who.name))
			
			elif self.decision == "love":
				i.reproduce(self.who)
				
				i.chanceToBefriend += 5
				i.chanceToFight -= 5
				
				self.createEntity()
			
			elif self.decision == "fight":
				i.chanceToFight += 5
				i.chanceToBefriend -= 5
								
				self.listOfKreatures.remove(self.who)
				i.fight(self.who)
			
			elif self.decision == "befriend":
				i.chanceToBefriend += 5
				i.chanceToFight -= 5
				
				i.befriend(self.who)
				
	def createEntity(self):
		self.creature = Entity(self.listOfRandomNames[random.randint(0,len(self.listOfRandomNames) - 1)])
		self.listOfKreatures.append(self.creature)