# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
from entity.livingEntity import LivingEntity
import random


# @author Daniel McCoy Stephenson
# @since 2017
class World(object):
    def __init__(self):
        self.entities = []

        # create ten creatures for the world to have to start with
        self.Alison = LivingEntity("Alison")
        self.Barry = LivingEntity("Barry")
        self.Conrad = LivingEntity("Conrad")
        self.Derrick = LivingEntity("Derrick")
        self.Eric = LivingEntity("Eric")
        self.Francis = LivingEntity("Francis")
        self.Gary = LivingEntity("Gary")
        self.Harry = LivingEntity("Harry")
        self.Isabelle = LivingEntity("Isabelle")
        self.Jasper = LivingEntity("Jasper")

        self.starterEntities = [
            "placeholder",
            self.Alison,
            self.Barry,
            self.Conrad,
            self.Derrick,
            self.Eric,
            self.Francis,
            self.Gary,
            self.Harry,
            self.Isabelle,
            self.Jasper,
        ]

        for entity in self.starterEntities:
            self.addEntity(entity)

    def addEntity(self, entity):
        self.entities.append(entity)

    def removeEntity(self, entity):
        self.entities.remove(entity)

    def getNumEntities(self):
        return len(self.entities)

    def getEntities(self):
        return self.entities

    def getRandomEntity(self):
        return self.entities[random.randint(0, len(self.entities) - 1)]
