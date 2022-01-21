from kreature import Kreature
import random
import time

class Simulation(object):
	
	def __init__(self):
				
		# creates ten creatures for the world to have to start with
		self.Alison = Kreature("Alison")
		self.Barry = Kreature("Barry")
		self.Conrad = Kreature("Conrad")
		self.Derrick = Kreature("Derrick")
		self.Eric = Kreature("Eric")
		self.Francis = Kreature("Francis")
		self.Gary = Kreature("Gary")
		self.Harry = Kreature("Harry")
		self.Isabelle = Kreature("Isabelle")
		self.Jasper = Kreature("Jasper")
		
		self.listOfKreatures = ["placholder", self.Alison, self.Barry, self.Conrad, self.Derrick, self.Eric,
						    self.Francis, self.Gary, self.Harry, self.Isabelle, self.Jasper]
						    
		self.listOfRandomNames = ["Jesse", "Juan", "Jose", "Ralph", "Jeremy", "Bobby", "Johnny", "Douglas", "Peter", "Scott", "Kyle", "Billy", "Terry", "Randy", "Adam"]
					
	def start(self):
		print("What would you like to name your kreature?\n")
		
		self.creatureName = input("> ")
		
		self.playerCreature = Kreature(self.creatureName)
		
		self.listOfKreatures[0] = self.playerCreature
		
		print("\n")
		
		# code to run a day, then show any new additions to log
		while True:
			try:
				print(self.playerCreature.log[0]) # tries to print log entry
				
				if "eaten" in self.playerCreature.log[0]: # if creature was eaten, break out of loop
					break
				
				del self.playerCreature.log[0] # tries to delete log entry
			
			except: # if list is empty, just keep going
				pass
			
			self.everyoneGo()
			
			time.sleep(1)
			
		if self.playerCreature.chanceToFight > self.playerCreature.chanceToBefriend:
			print("\n%s was ferocious." % self.playerCreature.name)
		
		elif self.playerCreature.chanceToBefriend > self.playerCreature.chanceToFight:
			print("\n%s was very friendly." % self.playerCreature.name)
		
		input("\n[CONTINUE]")
		print("\n----------------------------\n"	)
		print("Friendships forged: %d" % self.playerCreature.friendsMade)
		print("Babies made: %d" % self.playerCreature.babiesMade)
		print("Creatures Eaten: %d" % self.playerCreature.creaturesEaten)
		
		print("\n----------------------------\n")
		print("%s's chance to get into a fight was %d percent." % (self.playerCreature.name, self.playerCreature.chanceToFight))
		print("%s's chance to be nice was %d percent." % (self.playerCreature.name, self.playerCreature.chanceToBefriend))
		
		print("\n----------------------------\n")
		print("Kreatures still alive: %d" % len(self.listOfKreatures))	
				
	def everyoneGo(self):
		for i in self.listOfKreatures:
			self.who = self.listOfKreatures[random.randint(0,len(self.listOfKreatures) - 1)]
			
			if self.who == i:
				continue
			
			self.decision = i.decideWhatToDo(self.who)
			
			if self.decision == "nothing":
				i.log.append("%s had an argument with %s!" % (i.name, self.who.name))
			
			elif self.decision == "love":
				i.love(self.who)
				
				i.chanceToBefriend += 5
				i.chanceToFight -= 5
				
				self.makeBaby()
			
			elif self.decision == "fight":
				i.chanceToFight += 5
				i.chanceToBefriend -= 5
								
				self.listOfKreatures.remove(self.who)
				i.fight(self.who)
			
			elif self.decision == "befriend":
				i.chanceToBefriend += 5
				i.chanceToFight -= 5
				
				i.befriend(self.who)
				
	def makeBaby(self):
		self.creature = Kreature(self.listOfRandomNames[random.randint(0,len(self.listOfRandomNames) - 1)])
		self.listOfKreatures.append(self.creature)

mySim = Simulation()
mySim.start()
