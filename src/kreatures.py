# Copyright (c) 2022 Daniel McCoy Stephenson
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

        self.names = [
            "Jesse",
            "Juan",
            "Jose",
            "Ralph",
            "Jeremy",
            "Bobby",
            "Johnny",
            "Douglas",
            "Peter",
            "Scott",
            "Kyle",
            "Billy",
            "Terry",
            "Randy",
            "Adam",
        ]

        print("What would you like to name your kreature?")
        self.creatureName = input("> ")
        self.playerCreature = LivingEntity(self.creatureName)

        self.running = True
        self.config = Config()
        self.tick = 0
        
        # Initialize player early-game protection
        self.playerCreature.damageReduction = self.config.playerDamageReduction
        self.playerCreature.log.append("%s has early-game protection!" % self.playerCreature.name)

    def initiateEntityActions(self):
        entities_to_remove = []  # Track entities that die this turn

        for entity in self.environment.getEntities():
            target = self.environment.getRandomEntity()

            if target == entity:
                continue

            decision = entity.getNextAction(target)

            if decision == "nothing":
                entity.log.append(
                    "%s had an argument with %s!" % (entity.name, target.name)
                )
            elif decision == "love":
                parents = entity.reproduce(target)
                entity.increaseChanceToBefriend()
                entity.decreaseChanceToFight()
                self.createChildEntity(parents[0], parents[1])
            elif decision == "fight":
                # Enhanced protection: during grace period, reduce attacks on player
                if target == self.playerCreature:
                    if self.config.godMode:
                        continue
                    # During grace period, 85% chance to skip attacking the player
                    if (self.tick < self.config.earlyGameGracePeriod and 
                        random.randint(1, 100) <= 85):
                        entity.log.append(
                            "%s decided not to attack %s." % (entity.name, target.name)
                        )
                        continue
                
                entity.increaseChanceToFight()
                entity.decreaseChanceToBefriend()
                entity.fight(target)
                # Check if either entity died from the fight to the death
                if not target.isAlive() and target not in entities_to_remove:
                    entities_to_remove.append(target)
                if not entity.isAlive() and entity not in entities_to_remove:
                    entities_to_remove.append(entity)
            elif decision == "befriend":
                entity.increaseChanceToBefriend()
                entity.decreaseChanceToFight()
                entity.befriend(target)

        # Remove all entities that died this turn
        for entity in entities_to_remove:
            self.environment.removeEntity(entity)

    def updatePlayerProtection(self):
        """Update player protection based on current tick"""
        if self.tick >= self.config.earlyGameGracePeriod:
            # Grace period has ended
            if hasattr(self.playerCreature, 'damageReduction') and self.playerCreature.damageReduction > 0:
                self.playerCreature.damageReduction = 0
                self.playerCreature.log.append("%s's protection has worn off!" % self.playerCreature.name)

    def regenerateAllEntities(self):
        """Regenerate health for all living entities"""
        for entity in self.environment.getEntities():
            if entity.isAlive():
                entity.regenerateHealth()

    def createEntity(self):
        newEntity = LivingEntity(self.names[random.randint(0, len(self.names) - 1)])
        self.environment.addEntity(newEntity)

    def createChildEntity(self, parent1, parent2):
        """Create a child entity with proper parent-child relationships"""
        childName = self.names[random.randint(0, len(self.names) - 1)]
        child = LivingEntity(childName)

        # Set up parent-child relationships
        child.addParent(parent1)
        child.addParent(parent2)
        parent1.addChild(child)
        parent2.addChild(child)

        # Child inherits some traits from parents (average)
        child.chanceToFight = (parent1.chanceToFight + parent2.chanceToFight) // 2
        child.chanceToBefriend = 100 - child.chanceToFight

        # Child inherits health traits from parents (average with some variation)
        parentHealthAvg = (parent1.maxHealth + parent2.maxHealth) // 2
        child.health = parentHealthAvg + random.randint(-10, 10)  # Add some variation
        child.maxHealth = child.health

        child.log.append(
            "%s is the child of %s and %s." % (childName, parent1.name, parent2.name)
        )

        self.environment.addEntity(child)
        return child

    def getLivingChildren(self, entity):
        """Get all living children of an entity"""
        living_children = []
        for child in entity.children:
            if child in self.environment.entities:
                living_children.append(child)
        return living_children

    def continueAsChild(self):
        """Allow player to continue as one of their creature's children"""
        living_children = self.getLivingChildren(self.playerCreature)

        if not living_children:
            return False

        print(
            f"\n{self.playerCreature.name} has died, but has {len(living_children)} living children!"
        )
        print("Would you like to continue as one of your children? (y/n)")
        choice = input("> ").lower().strip()

        if choice == "y" or choice == "yes":
            if len(living_children) == 1:
                # Only one child, automatically select it
                new_player = living_children[0]
                print(f"You are now playing as {new_player.name}!")
            else:
                # Multiple children, let player choose
                print("\nWhich child would you like to continue as?")
                for i, child in enumerate(living_children):
                    print(f"{i+1}. {child.name}")

                while True:
                    try:
                        choice_idx = int(input("> ")) - 1
                        if 0 <= choice_idx < len(living_children):
                            new_player = living_children[choice_idx]
                            print(f"You are now playing as {new_player.name}!")
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a number.")

            # Update the player creature reference
            self.playerCreature = new_player
            # Make sure the new player creature is at position 0 in the entities list
            if new_player in self.environment.entities:
                self.environment.entities.remove(new_player)
            self.environment.entities.insert(0, new_player)
            self.running = True  # Continue the game
            return True

        return False

    def printSummary(self):
        print("=== Summary ===")
        if self.playerCreature.chanceToFight > self.playerCreature.chanceToBefriend:
            print("%s was ferocious." % self.playerCreature.name)
        elif self.playerCreature.chanceToBefriend > self.playerCreature.chanceToFight:
            print("%s was very friendly." % self.playerCreature.name)
        else:
            print("%s was neutral." % self.playerCreature.name)
        print(
            "%s's chance to get into a fight was %d percent."
            % (self.playerCreature.name, self.playerCreature.chanceToFight)
        )
        print(
            "%s's chance to be nice was %d percent."
            % (self.playerCreature.name, self.playerCreature.chanceToBefriend)
        )
        
        # Show protection status
        if hasattr(self.playerCreature, 'damageReduction') and self.playerCreature.damageReduction > 0:
            protection_percent = int(self.playerCreature.damageReduction * 100)
            print("%s still has %d%% damage reduction." % (self.playerCreature.name, protection_percent))
        
        if self.playerCreature.isAlive():
            print(
                "%s ended with %d health (out of %d max)."
                % (
                    self.playerCreature.name,
                    self.playerCreature.health,
                    self.playerCreature.maxHealth,
                )
            )
        else:
            print("%s died during the simulation." % self.playerCreature.name)
        print("Kreatures still alive: %d" % self.environment.getNumEntities())
        print("Simulation ran for %d ticks." % self.tick)

    def printStats(self):
        print("=== Stats ===")
        print("Friendships forged: %d" % self.playerCreature.stats.numFriendshipsForged)
        print("Babies made: %d" % self.playerCreature.stats.numOffspring)
        print("Creatures Eaten: %d" % self.playerCreature.stats.numCreaturesEaten)

    def run(self):
        self.environment.entities[0] = self.playerCreature
        print("")

        # code to run a day, then show any new additions to log
        while self.running:
            try:
                print(self.playerCreature.log[0])  # tries to print log entry
                if (
                    "eaten" in self.playerCreature.log[0]
                ):  # if creature was eaten, check for children
                    if not self.continueAsChild():
                        self.running = False
                        break
                del self.playerCreature.log[0]  # tries to delete log entry
            except:  # if list is empty, just keep going
                pass

            self.initiateEntityActions()
            self.updatePlayerProtection()  # Update player protection status
            self.regenerateAllEntities()  # Regenerate health for all entities
            time.sleep(self.config.tickLength)
            self.tick += 1
            if self.tick >= self.config.maxTicks:
                print("Maximum iterations reached.")
                self.running = False
                break

        input("[CONTINUE]")

        self.printSummary()
        self.printStats()


kreatures = Kreatures()
kreatures.run()
