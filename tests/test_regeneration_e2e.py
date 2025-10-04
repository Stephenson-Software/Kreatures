# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0

"""
End-to-end test to verify health regeneration behavior in a realistic game scenario.

This test simulates a realistic game scenario where:
1. An entity gets damaged in combat
2. The entity continues taking actions while health is low
3. Health regenerates passively over time
4. The entity never becomes idle due to regeneration
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import unittest
from unittest.mock import patch
from entity.livingEntity import LivingEntity


class TestRealisticGameScenario(unittest.TestCase):
    """End-to-end test simulating realistic game scenarios"""

    def test_entity_damaged_in_combat_continues_acting_while_regenerating(self):
        """
        Realistic scenario: Entity gets damaged in fight, then continues taking
        actions while passively regenerating health.
        """
        # Setup: Two entities
        entity = LivingEntity("Fighter")
        opponent1 = LivingEntity("Opponent1")
        opponent2 = LivingEntity("Opponent2")
        friend = LivingEntity("Friend")

        # Make them friends so they can reproduce later
        entity.friends.append(friend)
        friend.friends.append(entity)

        # Phase 1: Entity gets damaged in combat
        initial_health = entity.health
        entity.health -= 40  # Simulate damage from combat
        damaged_health = entity.health

        self.assertLess(damaged_health, initial_health, "Entity should be damaged")

        # Phase 2: Entity continues taking actions while damaged
        # This simulates multiple game ticks where entity acts, then regenerates

        actions_taken = []
        health_progression = [damaged_health]

        for tick in range(20):
            # Step 1: Entity makes decision and takes action (like initiateEntityActions())
            if tick < 5:
                # First 5 ticks: fight different opponents
                target = opponent1 if tick % 2 == 0 else opponent2
                with patch("random.randint") as mock_random:
                    mock_random.return_value = 30  # Fight action
                    decision = entity.getNextAction(target)
                    actions_taken.append(("fight", tick))
            elif tick < 10:
                # Next 5 ticks: befriend others
                with patch("random.randint") as mock_random:
                    mock_random.return_value = 70  # Befriend action
                    decision = entity.getNextAction(opponent1)
                    if decision == "befriend":
                        actions_taken.append(("befriend", tick))
                    elif decision == "love":
                        actions_taken.append(("love", tick))
            else:
                # Last 10 ticks: reproduce with friend
                with patch("random.randint") as mock_random:
                    mock_random.return_value = 70  # Love action (with friend)
                    decision = entity.getNextAction(friend)
                    if decision == "love":
                        actions_taken.append(("love", tick))

            # Step 2: Passive health regeneration (like regenerateAllEntities())
            with patch("random.randint") as mock_random:
                # 30% chance to regenerate (simulate realistic probability)
                if tick % 3 == 0:  # Trigger every 3rd tick for testing
                    mock_random.side_effect = [2, 2]
                    entity.regenerateHealth()
                else:
                    mock_random.return_value = 5  # Don't trigger
                    entity.regenerateHealth()

            health_progression.append(entity.health)

        # Verification 1: Entity took actions every tick
        self.assertEqual(
            len(actions_taken),
            20,
            "Entity should take action every tick regardless of health",
        )

        # Verification 2: Entity's health increased over time from regeneration
        final_health = entity.health
        self.assertGreater(
            final_health,
            damaged_health,
            "Health should increase from regeneration over time",
        )

        # Verification 3: Entity took diverse actions (not stuck in one behavior)
        action_types = set([action[0] for action in actions_taken])
        self.assertGreater(
            len(action_types), 1, "Entity should take different types of actions"
        )

        # Verification 4: Actions were taken while health was below max
        # (proves regeneration didn't block actions)
        actions_while_damaged = [
            action
            for action in actions_taken
            if health_progression[action[1]] < entity.maxHealth
        ]
        self.assertGreater(
            len(actions_while_damaged),
            10,
            "Many actions should be taken while health is still regenerating",
        )

        # Verification 5: Entity remained functional throughout
        self.assertTrue(entity.isAlive())
        self.assertGreater(entity.stats.numActionsTaken, 15)

    def test_entity_at_full_health_continues_acting(self):
        """
        Test that entity at full health doesn't become idle.
        This verifies there's no "regeneration complete → stop acting" logic.
        """
        entity = LivingEntity("HealthyEntity")
        target = LivingEntity("Target")

        # Entity is at full health
        entity.health = entity.maxHealth

        # Take 10 actions
        for tick in range(10):
            # Regeneration call (should do nothing at full health)
            entity.regenerateHealth()

            # Entity should still be able to take actions
            with patch("random.randint") as mock_random:
                mock_random.return_value = 70
                decision = entity.getNextAction(target)

            self.assertIn(decision, ["fight", "befriend", "love", "nothing"])

        # Entity should have taken all 10 actions
        self.assertEqual(entity.stats.numActionsTaken, 10)
        self.assertEqual(entity.health, entity.maxHealth)

    def test_multiple_entities_regenerate_and_act_independently(self):
        """
        Test that multiple entities can regenerate and act independently,
        as would happen in the actual game loop.
        """
        entities = [LivingEntity(f"Entity{i}") for i in range(5)]

        # Damage all entities differently
        for i, entity in enumerate(entities):
            entity.health -= (i + 1) * 10

        # Simulate 10 ticks
        for tick in range(10):
            for entity in entities:
                # Each entity takes an action
                target = entities[(entities.index(entity) + 1) % len(entities)]
                with patch("random.randint") as mock_random:
                    mock_random.return_value = 70
                    entity.getNextAction(target)

                # Each entity regenerates
                with patch("random.randint") as mock_random:
                    if tick % 2 == 0:
                        mock_random.side_effect = [2, 2]
                        entity.regenerateHealth()
                    else:
                        mock_random.return_value = 5
                        entity.regenerateHealth()

        # All entities should have taken actions
        for entity in entities:
            self.assertGreater(entity.stats.numActionsTaken, 5)
            self.assertTrue(entity.isAlive())


if __name__ == "__main__":
    unittest.main()
