# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0

import sys
import os
import unittest
from unittest.mock import patch

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.livingEntity import LivingEntity


class TestHealthRegenerationBehavior(unittest.TestCase):
    """Test suite to verify health regeneration is a passive background process"""

    def test_entity_continues_making_decisions_while_regenerating(self):
        """Test that entities continue to take actions even when health is below max"""
        entity = LivingEntity("TestEntity")
        target = LivingEntity("TargetEntity")

        # Reduce entity's health to trigger potential regeneration
        entity.health = entity.maxHealth - 20

        # Entity should still be able to make decisions
        with patch("random.randint") as mock_random:
            # First call for getNextAction decision (50 = fight)
            # Subsequent calls for other random operations
            mock_random.side_effect = [50, 10, 10, 10, 10]

            decision = entity.getNextAction(target)

            # Entity should make a decision even with low health
            self.assertIn(decision, ["fight", "befriend", "love", "nothing"])

            # Stats should be updated (indicating action was taken)
            self.assertGreater(entity.stats.numActionsTaken, 0)

    def test_entity_continues_making_decisions_after_full_health(self):
        """Test that entities don't become idle after reaching full health"""
        entity = LivingEntity("TestEntity")
        target = LivingEntity("TargetEntity")

        # Set entity to full health
        entity.health = entity.maxHealth

        # Entity should still be able to make decisions at full health
        with patch("random.randint") as mock_random:
            # Set up to return befriend action
            mock_random.return_value = 80  # Greater than typical chanceToFight

            decision = entity.getNextAction(target)

            # Entity should make a decision at full health
            self.assertIn(decision, ["fight", "befriend", "love", "nothing"])

    def test_regeneration_does_not_prevent_fighting(self):
        """Test that entities can fight while regenerating health"""
        attacker = LivingEntity("Attacker")
        defender = LivingEntity("Defender")

        # Reduce attacker's health
        attacker.health = attacker.maxHealth - 30
        defender.health = 50  # Low enough to be killed in fight

        # Store original health
        attacker.health

        # Attacker should still be able to fight
        with patch("random.randint") as mock_random:
            # Set damage values to ensure defender dies
            mock_random.return_value = 60

            attacker.fight(defender)

            # Fight should have occurred (defender should be dead or damaged)
            self.assertLessEqual(defender.health, 0)

            # Attacker should have log entries about the fight
            fight_logs = [log for log in attacker.log if "fought" in log.lower()]
            self.assertGreater(len(fight_logs), 0)

    def test_regeneration_does_not_prevent_befriending(self):
        """Test that entities can befriend while regenerating health"""
        entity1 = LivingEntity("Entity1")
        entity2 = LivingEntity("Entity2")

        # Reduce entity1's health
        entity1.health = entity1.maxHealth - 25

        # Entity should still be able to befriend
        entity1.befriend(entity2)

        # Befriending should have occurred
        self.assertIn(entity2, entity1.friends)
        self.assertIn(entity1, entity2.friends)
        self.assertEqual(entity1.stats.numFriendshipsForged, 1)

    def test_regeneration_does_not_prevent_reproduction(self):
        """Test that entities can reproduce while regenerating health"""
        parent1 = LivingEntity("Parent1")
        parent2 = LivingEntity("Parent2")

        # Reduce parent1's health
        parent1.health = parent1.maxHealth - 40

        # Parents should still be able to reproduce
        result = parent1.reproduce(parent2)

        # Reproduction should return both parents
        self.assertEqual(result, (parent1, parent2))

        # Stats should be updated
        self.assertEqual(parent1.stats.numOffspring, 1)
        self.assertEqual(parent2.stats.numOffspring, 1)

    def test_regeneration_happens_independently_of_actions(self):
        """Test that regeneration is called independently of entity actions"""
        entity = LivingEntity("TestEntity")
        target = LivingEntity("TargetEntity")

        # Reduce entity's health
        entity.health = entity.maxHealth - 30
        original_health = entity.health

        # Make entity take an action
        with patch("random.randint") as mock_random:
            mock_random.return_value = 80  # Befriend action
            entity.getNextAction(target)

        # Now call regeneration separately (as the game loop does)
        with patch("random.randint") as mock_random:
            # Set to trigger regeneration (roll <= 3) and heal 2 HP
            mock_random.side_effect = [2, 2]
            entity.regenerateHealth()

        # Entity should have regenerated health
        self.assertGreater(entity.health, original_health)

        # And should still have taken an action
        self.assertGreater(entity.stats.numActionsTaken, 0)

    def test_multiple_actions_between_regeneration_ticks(self):
        """Test that entity can take multiple actions while health is regenerating"""
        entity = LivingEntity("TestEntity")
        target1 = LivingEntity("Target1")
        target2 = LivingEntity("Target2")

        # Reduce entity's health
        entity.health = entity.maxHealth - 50
        entity.health

        # Simulate multiple ticks where entity takes actions
        action_count = 0
        for _ in range(5):
            with patch("random.randint") as mock_random:
                mock_random.return_value = 80  # Befriend action
                decision = entity.getNextAction(
                    target1 if action_count % 2 == 0 else target2
                )
                if decision in ["fight", "befriend", "love"]:
                    action_count += 1

        # Entity should have taken multiple actions
        self.assertGreater(entity.stats.numActionsTaken, 1)

        # Health may or may not have changed (regeneration is probabilistic)
        # But entity should still be functional
        self.assertTrue(entity.isAlive())

    def test_regeneration_at_full_health_does_not_block_actions(self):
        """Test that entity at full health can still take actions"""
        entity = LivingEntity("TestEntity")
        target = LivingEntity("TargetEntity")

        # Entity is at full health
        self.assertEqual(entity.health, entity.maxHealth)

        # Call regeneration (should do nothing as health is full)
        with patch("random.randint") as mock_random:
            mock_random.return_value = 1  # Would trigger regeneration if needed
            entity.regenerateHealth()

        # Entity should still be able to take actions after regeneration call
        with patch("random.randint") as mock_random:
            mock_random.return_value = 70
            decision = entity.getNextAction(target)

        self.assertIn(decision, ["fight", "befriend", "love", "nothing"])
        self.assertGreater(entity.stats.numActionsTaken, 0)

    def test_regeneration_logs_do_not_interfere_with_action_logs(self):
        """Test that regeneration logs are separate from action logs"""
        entity = LivingEntity("TestEntity")
        target = LivingEntity("TargetEntity")

        # Reduce health to trigger regeneration
        entity.health = entity.maxHealth - 20

        # Clear creation log
        entity.log.clear()

        # Trigger regeneration
        with patch("random.randint") as mock_random:
            # Trigger regeneration (roll <= 3) with significant heal (>= 2)
            mock_random.side_effect = [2, 3]
            entity.regenerateHealth()

        regen_log_count = len(entity.log)

        # Take an action
        with patch("random.randint") as mock_random:
            mock_random.return_value = 70
            entity.getNextAction(target)

        entity.befriend(target)

        # Should have both regeneration and action logs
        self.assertGreater(len(entity.log), regen_log_count)


class TestHealthRegenerationMechanism(unittest.TestCase):
    """Test suite for the regeneration mechanism itself"""

    def test_regeneration_heals_partial_health(self):
        """Test that regeneration heals between 1-3 health per successful tick"""
        entity = LivingEntity("TestEntity")
        entity.health = entity.maxHealth - 50
        original_health = entity.health

        # Force successful regeneration
        with patch("random.randint") as mock_random:
            # First call: trigger regeneration (roll <= 3)
            # Second call: heal amount (1-3)
            mock_random.side_effect = [2, 2]
            entity.regenerateHealth()

        # Should have healed
        self.assertEqual(entity.health, original_health + 2)

    def test_regeneration_does_not_exceed_max_health(self):
        """Test that regeneration caps at max health"""
        entity = LivingEntity("TestEntity")
        entity.health = entity.maxHealth - 1

        # Force regeneration with high heal amount
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [2, 10]  # Large heal
            entity.regenerateHealth()

        # Should not exceed max health
        self.assertEqual(entity.health, entity.maxHealth)

    def test_regeneration_probabilistic_nature(self):
        """Test that regeneration has ~30% chance per tick"""
        entity = LivingEntity("TestEntity")
        entity.health = entity.maxHealth - 50

        # Test that rolls > 3 don't trigger regeneration
        with patch("random.randint") as mock_random:
            mock_random.return_value = 5  # > 3, should not trigger
            original_health = entity.health
            entity.regenerateHealth()

        # Should not have healed
        self.assertEqual(entity.health, original_health)


class TestHealthRegenerationIntegration(unittest.TestCase):
    """Integration tests for health regeneration with game loop simulation"""

    def test_entities_take_actions_across_multiple_ticks_while_regenerating(self):
        """Test that entities continue taking actions across multiple game ticks while health regenerates"""
        entity = LivingEntity("TestEntity")
        target = LivingEntity("TargetEntity")

        # Reduce health significantly
        entity.health = entity.maxHealth - 50
        initial_health = entity.health

        # Simulate 10 game ticks (like the game loop does)
        action_count = 0
        regen_count = 0

        for tick in range(10):
            # Step 1: Entity takes an action (initiateEntityActions)
            with patch("random.randint") as mock_random:
                mock_random.return_value = 70  # Befriend action
                decision = entity.getNextAction(target)
                if decision in ["fight", "befriend", "love"]:
                    action_count += 1

            # Step 2: Entity regenerates health (regenerateAllEntities)
            old_health = entity.health
            with patch("random.randint") as mock_random:
                # Trigger regeneration every 3rd tick
                if tick % 3 == 0:
                    mock_random.side_effect = [2, 2]
                    entity.regenerateHealth()
                    if entity.health > old_health:
                        regen_count += 1
                else:
                    mock_random.return_value = 5  # Don't trigger
                    entity.regenerateHealth()

        # Verify entity took actions every tick
        self.assertEqual(action_count, 10, "Entity should take action every tick")

        # Verify health increased from regeneration
        self.assertGreater(
            entity.health, initial_health, "Health should have increased"
        )

        # Verify regeneration happened
        self.assertGreater(regen_count, 0, "Regeneration should have occurred")

        # Verify entity continued functioning
        self.assertTrue(entity.isAlive())
        self.assertEqual(entity.stats.numActionsTaken, 10)

    def test_game_tick_order_actions_then_regeneration(self):
        """Test that game tick order is: actions first, then regeneration"""
        entity = LivingEntity("TestEntity")
        target = LivingEntity("TargetEntity")

        # Reduce health
        entity.health = entity.maxHealth - 30

        # Clear log
        entity.log.clear()

        # Simulate one game tick with specific order
        # Step 1: Take action
        with patch("random.randint") as mock_random:
            mock_random.return_value = 70
            entity.getNextAction(target)
        entity.befriend(target)

        action_log_count = len(entity.log)

        # Step 2: Regenerate (happens after action)
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [2, 3]  # Trigger regeneration
            entity.regenerateHealth()

        total_log_count = len(entity.log)

        # Both action and regeneration logs should exist
        self.assertGreater(action_log_count, 0, "Action should be logged")
        self.assertGreater(
            total_log_count, action_log_count, "Regeneration should also be logged"
        )

        # Stats should show action was taken
        self.assertGreater(entity.stats.numActionsTaken, 0)


if __name__ == "__main__":
    unittest.main()
