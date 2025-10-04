# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
import random
from flags.flags import Flags
from stats.stats import Stats


# @author Daniel McCoy Stephenson
# @since 2017
class LivingEntity(object):
    def __init__(self, name):
        self.name = name
        self.chanceToFight = random.randint(45, 55)  # Back to normal values
        self.chanceToBefriend = 100 - self.chanceToFight
        self.health = random.randint(80, 120)  # Health between 80-120
        self.maxHealth = self.health  # Track maximum health for potential future use
        self.log = ["%s was created." % self.name]
        self.friends = []
        self.stats = Stats()
        self.flags = Flags()
        self.parents = []  # Track parent entities
        self.children = []  # Track child entities

    def rollForMovement(self):
        if random.randint(1, 10) == 1:
            return True
        else:
            return False

    def getNextAction(self, kreature):
        self.decision = random.randint(0, 100)
        if self.decision <= self.chanceToFight:  # if fight
            for i in self.friends:
                if i.name == kreature.name:
                    return "nothing"  # if creature is a friend, don't fight
            self.stats.numActionsTaken += 1
            return "fight"  # if search comes up empty, fight
        elif self.chanceToFight < self.decision:  # if befriend
            for i in self.friends:
                if i.name == kreature.name:
                    self.stats.numActionsTaken += 1
                    return "love"  # if creature is a friend, have a baby
            self.stats.numActionsTaken += 1
            return "befriend"

    def reproduce(self, kreature):
        self.log.append("%s made a baby with %s!" % (self.name, kreature.name))
        kreature.log.append("%s made a baby with %s!" % (kreature.name, self.name))
        self.stats.numOffspring += 1
        kreature.stats.numOffspring += 1
        # Return the parent entities so the child can be created with proper references
        return (self, kreature)

    def fight(self, kreature):
        # Fight to the death - continue until one creature dies
        while self.health > 0 and kreature.health > 0:
            # This creature attacks first
            if self.health > 0:
                damage = random.randint(15, 25)  # Random damage between 15-25
                # Apply damage reduction if target has it
                if (
                    hasattr(kreature, "damageReduction")
                    and kreature.damageReduction > 0
                ):
                    damage = int(damage * (1 - kreature.damageReduction))
                    damage = max(damage, 1)  # Ensure at least 1 damage

                kreature.health -= damage
                if kreature.health <= 0:
                    self.log.append(
                        "%s fought and ate %s!" % (self.name, kreature.name)
                    )
                    kreature.log.append(
                        "%s was eaten by %s!" % (kreature.name, self.name)
                    )
                    self.stats.numCreaturesEaten += 1
                    break
                else:
                    self.log.append(
                        "%s fought %s and dealt %d damage!"
                        % (self.name, kreature.name, damage)
                    )
                    kreature.log.append(
                        "%s took %d damage from %s! Health: %d"
                        % (kreature.name, damage, self.name, kreature.health)
                    )

            # Target creature counter-attacks if still alive
            if kreature.health > 0:
                damage = random.randint(15, 25)  # Random damage between 15-25
                # Apply damage reduction if target has it
                if hasattr(self, "damageReduction") and self.damageReduction > 0:
                    damage = int(damage * (1 - self.damageReduction))
                    damage = max(damage, 1)  # Ensure at least 1 damage

                self.health -= damage
                if self.health <= 0:
                    kreature.log.append(
                        "%s fought and ate %s!" % (kreature.name, self.name)
                    )
                    self.log.append("%s was eaten by %s!" % (self.name, kreature.name))
                    kreature.stats.numCreaturesEaten += 1
                    break
                else:
                    kreature.log.append(
                        "%s fought %s and dealt %d damage!"
                        % (kreature.name, self.name, damage)
                    )
                    self.log.append(
                        "%s took %d damage from %s! Health: %d"
                        % (self.name, damage, kreature.name, self.health)
                    )

    def befriend(self, kreature):
        self.log.append("%s made friends with %s!" % (self.name, kreature.name))
        kreature.log.append("%s made friends with %s!" % (kreature.name, self.name))
        self.friends.append(kreature)
        kreature.friends.append(
            self
        )  # this should hopefully append this creature to kreature's friend list
        self.stats.numFriendshipsForged += 1
        kreature.stats.numFriendshipsForged += 1

    def increaseChanceToFight(self):
        self.chanceToFight += self.flags.increaseAmount
        if self.chanceToFight > 100:
            self.chanceToFight = 100

    def decreaseChanceToFight(self):
        self.chanceToFight -= self.flags.increaseAmount
        if self.chanceToFight < 0:
            self.chanceToFight = 0

    def increaseChanceToBefriend(self):
        self.chanceToBefriend += self.flags.increaseAmount
        if self.chanceToBefriend > 100:
            self.chanceToBefriend = 100

    def decreaseChanceToBefriend(self):
        self.chanceToBefriend -= self.flags.increaseAmount
        if self.chanceToBefriend < 0:
            self.chanceToBefriend = 0

    def addChild(self, child):
        """Add a child to this entity's children list"""
        self.children.append(child)

    def addParent(self, parent):
        """Add a parent to this entity's parents list"""
        self.parents.append(parent)

    def isAlive(self):
        """Check if the entity is still alive (health > 0)"""
        return self.health > 0

    def regenerateHealth(self):
        """Regenerate a small amount of health over time

        This is a passive background process that does not interfere with entity actions.
        Entities continue making decisions (fighting, befriending, reproducing) regardless
        of their health status or regeneration state. This method is called separately from
        getNextAction() to ensure regeneration happens alongside normal entity behavior.
        """
        if (
            self.health < self.maxHealth and random.randint(1, 10) <= 3
        ):  # 30% chance per tick
            regeneration = random.randint(1, 3)  # Regenerate 1-3 health per tick
            self.health = min(self.health + regeneration, self.maxHealth)
            # Only log significant regeneration events to avoid spam
            if regeneration >= 2:
                self.log.append(
                    "%s regenerated %d health! Health: %d/%d"
                    % (self.name, regeneration, self.health, self.maxHealth)
                )
