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
        if len(self.entities) == 0:
            return None
        return self.entities[random.randint(0, len(self.entities) - 1)]

    def cullWeakestEntities(self, targetCount, protectedEntity=None):
        """Remove the weakest entities to reduce population to targetCount"""
        if len(self.entities) <= targetCount:
            return []
        
        # Create list of entities that can be culled (excluding protected entity)
        cullable_entities = [e for e in self.entities if e != protectedEntity and hasattr(e, 'health')]
        
        if len(cullable_entities) == 0:
            return []
        
        # Sort by health (weakest first), then by number of children (fewer children first)
        cullable_entities.sort(key=lambda x: (x.health, len(getattr(x, 'children', []))))
        
        # Calculate how many to remove
        entities_to_remove = len(self.entities) - targetCount
        entities_to_remove = min(entities_to_remove, len(cullable_entities))
        
        # Remove the weakest entities
        removed_entities = []
        for i in range(entities_to_remove):
            entity = cullable_entities[i]
            self.removeEntity(entity)
            removed_entities.append(entity)
            
        return removed_entities
