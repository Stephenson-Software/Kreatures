# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import random
from unittest.mock import patch, MagicMock
from entity.livingEntity import LivingEntity
from world.world import World
from config.config import Config


class TestPopulationControl:
    """Test suite for population management and lag prevention"""

    def test_config_has_population_settings(self):
        """Test that config includes population control settings"""
        config = Config()
        assert hasattr(config, 'maxEntities')
        assert hasattr(config, 'entityCullThreshold')
        assert hasattr(config, 'entityLogMaxSize')
        assert config.maxEntities > 0
        assert 0 < config.entityCullThreshold < 1

    def test_entity_log_size_management(self):
        """Test that entity logs are kept within size limits"""
        entity = LivingEntity("TestEntity")
        
        # Add many log entries
        for i in range(100):
            entity.addLogEntry(f"Log entry {i}", maxLogSize=10)
        
        # Should only keep the most recent 10 entries
        assert len(entity.log) == 10
        assert "Log entry 99" in entity.log[-1]
        assert "Log entry 90" in entity.log[0]

    def test_world_cull_weakest_entities(self):
        """Test that world can cull weakest entities"""
        world = World()
        
        # Clear initial entities and add test entities with different health
        world.entities = []
        strong_entity = LivingEntity("Strong")
        strong_entity.health = 100
        weak_entity1 = LivingEntity("Weak1")
        weak_entity1.health = 10
        weak_entity2 = LivingEntity("Weak2")
        weak_entity2.health = 20
        
        world.addEntity(strong_entity)
        world.addEntity(weak_entity1)
        world.addEntity(weak_entity2)
        
        # Cull to 1 entity
        removed = world.cullWeakestEntities(1)
        
        assert len(removed) == 2
        assert len(world.entities) == 1
        assert world.entities[0] == strong_entity

    def test_world_cull_protects_player(self):
        """Test that culling protects the player entity"""
        world = World()
        world.entities = []
        
        player = LivingEntity("Player")
        player.health = 10  # Very weak
        other1 = LivingEntity("Other1")
        other1.health = 50
        other2 = LivingEntity("Other2")
        other2.health = 60
        
        world.addEntity(player)
        world.addEntity(other1)
        world.addEntity(other2)
        
        # Cull to 1, but protect player
        removed = world.cullWeakestEntities(1, protectedEntity=player)
        
        assert len(world.entities) == 1
        assert player in world.entities
        assert len(removed) == 2

    def test_world_get_random_entity_empty(self):
        """Test that getRandomEntity handles empty entity list"""
        world = World()
        world.entities = []
        
        result = world.getRandomEntity()
        assert result is None


class TestLagPreventionIntegration:
    """Test suite for integration scenarios with lag prevention"""

    def test_child_creation_respects_population_limit(self):
        """Test that child creation is blocked when population limit is reached"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                
                # World starts with 10 entities + player = 11, so set limit to current count
                initial_count = game.environment.getNumEntities()
                game.config.maxEntities = initial_count  # Set limit to current population
                
                # Try to create a child - should fail because we're at the limit
                parent1 = LivingEntity("Parent1")
                parent2 = LivingEntity("Parent2")
                
                child = game.createChildEntity(parent1, parent2)
                assert child is None
                
                # Population should stay at limit
                assert game.environment.getNumEntities() == game.config.maxEntities

    def test_population_management_triggers_culling(self):
        """Test that population management triggers culling when needed"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                
                # Set low limits to trigger culling
                game.config.maxEntities = 10
                game.config.entityCullThreshold = 0.8  # Cull at 8 entities
                
                # Add entities to trigger culling threshold
                while game.environment.getNumEntities() < 9:  # Above threshold
                    entity = LivingEntity("TestEntity")
                    entity.health = random.randint(10, 100)
                    game.environment.addEntity(entity)
                
                initial_count = game.environment.getNumEntities()
                
                # Trigger population management
                game.managePopulation()
                
                # Should have fewer entities now
                final_count = game.environment.getNumEntities()
                assert final_count < initial_count
                assert final_count <= int(game.config.maxEntities * 0.7)  # Target is 70% of max

    def test_can_create_new_entity_logic(self):
        """Test the logic for determining if new entities can be created"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                
                # Set limit higher than current count to allow creation
                current_count = game.environment.getNumEntities()
                game.config.maxEntities = current_count + 5
                
                # Should be able to create when under limit
                assert game.canCreateNewEntity() == True
                
                # Set limit to current count to block creation
                game.config.maxEntities = current_count
                
                # Should not be able to create when at limit
                assert game.canCreateNewEntity() == False


class TestPerformanceOptimizations:
    """Test suite for performance-related optimizations"""

    def test_entity_addlogentry_uses_config_limit(self):
        """Test that addLogEntry respects the configured log size limit"""
        config = Config()
        entity = LivingEntity("TestEntity")
        
        # Add more entries than the config limit
        for i in range(config.entityLogMaxSize + 20):
            entity.addLogEntry(f"Entry {i}", maxLogSize=config.entityLogMaxSize)
        
        # Should not exceed the configured limit
        assert len(entity.log) <= config.entityLogMaxSize

    def test_empty_entity_list_handling(self):
        """Test that empty entity lists are handled gracefully"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                
                # Clear all entities except player
                game.environment.entities = [game.playerCreature]
                
                # Should handle empty interactions gracefully
                game.initiateEntityActions()  # Should not crash
                
                assert len(game.environment.entities) == 1  # Player should remain


class TestWorldInitializationFix:
    """Test suite for the World initialization bug fix"""

    def test_world_starts_without_placeholder(self):
        """Test that World no longer includes 'placeholder' string in entities"""
        world = World()
        
        # All entities should be LivingEntity instances, not strings
        for entity in world.entities:
            assert isinstance(entity, LivingEntity)
            assert hasattr(entity, 'name')
            assert hasattr(entity, 'health')