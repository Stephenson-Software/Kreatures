import random

class Kreature(object):
	
	def __init__(self, name):
		self.name = name
		
		self.chanceToLove = 33.3
		self.chanceToFight = 33.3
		self.chanceToBefriend = 33.3
	
		self.log = ["%s was created." % self.name]
		
		self.friends = []
		
		self.babiesMade = 0
		self.creaturesEaten = 0
		self.friendsMade = 0
	
	def showLog(self):
		pass
	
	def decideIfToMove(self):
		if randint(1,10) == 1:
			return True
		else:
			return False
	
	def decideWhatToDo(self, kreature):
		self.decision = random.randint(0,100)
		
		if self.decision <= 0 + self.chanceToLove: # if love
			for i in self.friends:
				if i.name == kreature.name:
					return "love" # if creature is a friend, have a baby
					
			return "nothing"
		
		elif self.chanceToLove < self.decision < self.chanceToLove + self.chanceToFight: # if fight
			for i in self.friends:
				if i.name == kreature.name:
					return "nothing" # if creature is a friend, don't fight
			
			return "fight" # if search comes up empty, fight
		
		elif self.chanceToLove + self.chanceToFight < self.decision < 100: # if befriend
			for i in self.friends:
				if i.name == kreature.name:
					return "nothing" # if creature is a friend, do nothing
			
			return "befriend"
	
	def love(self, kreature):
		self.log.append("%s made a baby with %s!" % (self.name, kreature.name))
		kreature.log.append("%s made a baby with %s!" % (kreature.name, self.name))
		
		self.chanceToLove += 5
		self.chanceToFight -= 2.5
		self.chanceToBefriend -=2.5
	
	def fight(self, kreature):
		self.log.append("%s fought and ate %s!" % (self.name, kreature.name))
		kreature.log.append("%s was eaten by %s!" % (kreature.name, self.name))
		
		self.chanceToFight += 5
		self.chanceToLove -= 2.5
		self.chanceToBefriend -=2.5
		
	def befriend(self, kreature):
		self.log.append("%s made friends with %s!" % (self.name, kreature.name))
		kreature.log.append("%s made friends with %s!" % (kreature.name, self.name))
		
		self.friends.append(kreature)
		kreature.friends.append(self) # this should hopefully append this creature to kreature's friend list
		
		self.chanceToBefriend += 5
		self.chanceToLove -=2.5
		self.chanceToFight -= 2.5
