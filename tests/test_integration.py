# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0

import sys
import os
import unittest
from unittest.mock import patch

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.livingEntity import LivingEntity


class TestKreaturesIntegration(unittest.TestCase):
    """Integration test to verify the game works with expanded names"""

    @patch("builtins.input", return_value="TestPlayer")
    @patch("builtins.print")
    def setUp(self, mock_print, mock_input):
        """Set up test environment"""
        from kreatures import Kreatures

        self.kreatures = Kreatures()

    def test_create_multiple_entities_have_different_names(self):
        """Test that creating multiple entities can result in different names"""
        # Create several entities and collect their names
        entity_names = set()
        for _ in range(20):
            self.kreatures.createEntity()

        # Get names of all entities (excluding player creature and starter entities)
        # Filter out non-LivingEntity objects (like the "placeholder" string)
        for entity in self.kreatures.environment.getEntities():
            if hasattr(entity, "name") and entity != self.kreatures.playerCreature:
                entity_names.add(entity.name)

        # With 159 names available, we should see some variety
        # Even with random selection, getting 20+ different names should be likely
        self.assertGreater(
            len(entity_names), 1, "Should have at least some name variety"
        )

    def test_child_entities_get_names_from_expanded_list(self):
        """Test that child entities use names from the expanded list"""
        parent1 = LivingEntity("Parent1")
        parent2 = LivingEntity("Parent2")

        # Create multiple children to test name variety
        child_names = set()
        for _ in range(10):
            child = self.kreatures.createChildEntity(parent1, parent2)
            child_names.add(child.name)
            # Remove child to avoid cluttering the environment
            self.kreatures.environment.removeEntity(child)

        # All child names should be from our expanded list
        for name in child_names:
            self.assertIn(name, self.kreatures.names)

        # With 159 names, we should get some variety
        self.assertGreaterEqual(len(child_names), 1)

    def test_world_starter_entities_still_work(self):
        """Test that the world still initializes with starter entities correctly"""
        entities = self.kreatures.environment.getEntities()

        # Should have player creature plus starter entities from world
        self.assertGreater(len(entities), 1)

        # Verify starter entities have valid names
        starter_names = [
            "Alison",
            "Barry",
            "Conrad",
            "Derrick",
            "Eric",
            "Francis",
            "Gary",
            "Harry",
            "Isabelle",
            "Jasper",
        ]

        # Filter out non-LivingEntity objects (like the "placeholder" string)
        found_starter_names = [
            entity.name
            for entity in entities
            if hasattr(entity, "name") and entity.name in starter_names
        ]
        self.assertGreater(
            len(found_starter_names), 0, "Should find some starter entities"
        )


if __name__ == "__main__":
    unittest.main()
