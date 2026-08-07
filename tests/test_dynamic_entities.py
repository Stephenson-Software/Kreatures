# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import patch
from config.config import Config


class TestDynamicEntityLimits:
    """Test suite for dynamic entity limit adjustment based on performance"""

    def test_config_has_dynamic_settings(self):
        """Test that config includes dynamic performance settings"""
        config = Config()
        assert hasattr(config, 'maxEntities')
        assert hasattr(config, 'minEntities')
        assert hasattr(config, 'maxEntitiesLimit')
        assert hasattr(config, 'lagThreshold')
        assert hasattr(config, 'performanceWindow')
        
        # Check reasonable defaults
        assert config.minEntities < config.maxEntities < config.maxEntitiesLimit
        assert config.lagThreshold > 0
        assert config.performanceWindow > 0

    def test_performance_monitoring_initialization(self):
        """Test that Kreatures initializes performance monitoring"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                
                assert hasattr(game, 'tickTimes')
                assert isinstance(game.tickTimes, list)
                assert len(game.tickTimes) == 0

    def test_monitor_performance_tracks_times(self):
        """Test that performance monitoring tracks tick times"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                
                # Simulate some tick times
                game.monitorPerformance(0.01)  # Fast tick
                game.monitorPerformance(0.02)  # Another fast tick
                game.monitorPerformance(0.03)  # Slower tick
                
                assert len(game.tickTimes) == 3
                assert 0.01 in game.tickTimes
                assert 0.02 in game.tickTimes
                assert 0.03 in game.tickTimes

    def test_performance_window_limit(self):
        """Test that performance monitoring respects window size"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                game.config.performanceWindow = 3
                
                # Add more tick times than window size
                for i in range(5):
                    game.monitorPerformance(0.01 * (i + 1))
                
                # Should only keep the most recent window size
                assert len(game.tickTimes) == 3
                assert game.tickTimes == [0.03, 0.04, 0.05]

    def test_adjust_max_entities_reduces_on_lag(self):
        """Test that max entities is reduced when lag is detected"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print') as mock_print:
                game = Kreatures()
                initial_max = game.config.maxEntities
                
                # Simulate high lag (above threshold)
                lag_time = game.config.lagThreshold * 2  # Double the threshold
                game.adjustMaxEntitiesBasedOnLag(lag_time)
                
                # Max entities should be reduced
                assert game.config.maxEntities < initial_max
                assert game.config.maxEntities >= game.config.minEntities
                
                # Should print a message about reducing entities
                mock_print.assert_called()
                printed_text = str(mock_print.call_args)
                assert "lag detected" in printed_text.lower()
                assert "reducing" in printed_text.lower()

    def test_adjust_max_entities_increases_on_good_performance(self):
        """Test that max entities is increased when performance is good"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print') as mock_print:
                game = Kreatures()
                initial_max = game.config.maxEntities
                
                # Add some entities to make the system consider increasing limit
                from entity.livingEntity import LivingEntity
                for i in range(int(initial_max * 0.9)):  # Fill to 90% capacity
                    entity = LivingEntity(f"Entity{i}")
                    game.environment.addEntity(entity)
                
                # Simulate very good performance (well below threshold)
                good_time = game.config.lagThreshold * 0.25  # Quarter of the threshold
                game.adjustMaxEntitiesBasedOnLag(good_time)
                
                # Max entities should be increased (but not exceed limit)
                assert game.config.maxEntities >= initial_max
                assert game.config.maxEntities <= game.config.maxEntitiesLimit
                
                # Should print a message about increasing entities
                mock_print.assert_called()
                printed_text = str(mock_print.call_args)
                assert "good performance" in printed_text.lower()
                assert "increasing" in printed_text.lower()

    def test_max_entities_respects_hard_limits(self):
        """Test that max entities never goes below min or above hard limit"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                
                # Test lower bound - extreme lag
                extreme_lag_time = game.config.lagThreshold * 10
                for _ in range(10):  # Multiple adjustments
                    game.adjustMaxEntitiesBasedOnLag(extreme_lag_time)
                
                assert game.config.maxEntities >= game.config.minEntities
                
                # Reset and test upper bound - extreme good performance
                game.config.maxEntities = game.config.maxEntitiesLimit - 10
                from entity.livingEntity import LivingEntity
                for i in range(game.config.maxEntities):
                    entity = LivingEntity(f"Entity{i}")
                    game.environment.addEntity(entity)
                
                excellent_time = game.config.lagThreshold * 0.1
                for _ in range(10):  # Multiple adjustments
                    game.adjustMaxEntitiesBasedOnLag(excellent_time)
                
                assert game.config.maxEntities <= game.config.maxEntitiesLimit

    def test_no_adjustment_with_insufficient_data(self):
        """Test that no adjustment occurs without sufficient performance data"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                initial_max = game.config.maxEntities
                
                # Add only a few data points (less than 5)
                game.monitorPerformance(0.1)  # High lag time
                game.monitorPerformance(0.1)  # High lag time
                
                # Max entities should not change
                assert game.config.maxEntities == initial_max


class TestDynamicEntityIntegration:
    """Test suite for integration of dynamic entity limits with existing systems"""

    def test_dynamic_limits_work_with_population_management(self):
        """Test that dynamic limits integrate with existing population management"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                
                # Reduce max entities dynamically
                game.config.maxEntities = 30
                
                # Fill beyond the new limit
                from entity.livingEntity import LivingEntity
                for i in range(35):
                    entity = LivingEntity(f"Entity{i}")
                    game.environment.addEntity(entity)
                
                # Population management should respect the new dynamic limit
                game.managePopulation()
                
                # Should have culled based on the new limit
                assert game.environment.getNumEntities() <= game.config.maxEntities

    def test_child_creation_respects_dynamic_limits(self):
        """Test that child creation uses the current dynamic max entities"""
        from kreatures import Kreatures
        
        with patch('builtins.input', return_value='TestPlayer'):
            with patch('builtins.print'):
                game = Kreatures()
                
                # Dynamically reduce the limit to current population
                current_pop = game.environment.getNumEntities()
                game.config.maxEntities = current_pop
                
                # Try to create a child - should fail
                from entity.livingEntity import LivingEntity
                parent1 = LivingEntity("Parent1")
                parent2 = LivingEntity("Parent2")
                
                child = game.createChildEntity(parent1, parent2)
                assert child is None  # Should be blocked by dynamic limit