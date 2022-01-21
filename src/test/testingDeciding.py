 # Copyright (c) 2022 McCoy Software Solutions
 # Apache License 2.0
import random

chanceToLove = 33.3
chanceToFight = 33.3
chanceToBefriend = 33.3

decision = random.randint(0,100)

print("Chance To Love: %d" % chanceToLove)
print("Chance To Fight: %d" % chanceToFight)
print("Chance To Befriend: %d" % chanceToBefriend)

print("Decision: %d" % decision)

if decision <= 0 + chanceToLove:
	print("love")

elif chanceToLove < decision < chanceToLove + chanceToFight:
	print("fight")

elif chanceToLove + chanceToFight < decision < 100:
	print("befriend")
