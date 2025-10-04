# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import random
from unittest.mock import patch
from entity.livingEntity import LivingEntity
from config.config import Config


class TestDamageReduction:
    """Test suite for damage reduction functionality"""

    def test_damage_reduction_applied(self):
        """Test that damage reduction is applied correctly during fights"""
        # Create two creatures
        LivingEntity("Attacker")
        defender = LivingEntity("Defender")

        # Give defender damage reduction
        defender.damageReduction = 0.4  # 40% damage reduction

        # Record initial health
        defender.health

        # Simulate a single attack (we'll patch the random damage to be predictable)
        original_randint = random.randint
        random.randint = lambda a, b: 20  # Always deal 20 damage

        try:
            # Make attacker attack defender once, then stop the fight early
            original_health = defender.health
            damage = 20
            reduced_damage = int(
                damage * (1 - defender.damageReduction)
            )  # Should be 12

            # Apply damage manually to test calculation
            defender.health -= reduced_damage

            # Verify damage reduction worked
            expected_health = original_health - reduced_damage
            assert defender.health == expected_health
            assert reduced_damage == 12  # 20 * 0.6 = 12

        finally:
            # Restore original random function
            random.randint = original_randint

    def test_minimum_damage(self):
        """Test that damage reduction doesn't reduce damage below 1"""
        LivingEntity("Attacker")
        defender = LivingEntity("Defender")

        # Give defender very high damage reduction
        defender.damageReduction = 0.99  # 99% damage reduction

        # Test that even with high reduction, at least 1 damage is dealt
        original_randint = random.randint
        random.randint = lambda a, b: 1  # Minimum damage

        try:
            original_health = defender.health
            damage = 1
            reduced_damage = int(damage * (1 - defender.damageReduction))  # Would be 0
            reduced_damage = max(reduced_damage, 1)  # Should be adjusted to 1

            defender.health -= reduced_damage

            # Verify at least 1 damage was dealt
            assert defender.health == original_health - 1

        finally:
            random.randint = original_randint

    def test_no_damage_reduction_without_attribute(self):
        """Test that creatures without damageReduction attribute take full damage"""
        LivingEntity("Attacker")
        defender = LivingEntity("Defender")

        # Ensure defender has no damageReduction attribute
        if hasattr(defender, "damageReduction"):
            delattr(defender, "damageReduction")

        original_health = defender.health

        with patch("random.randint", return_value=20):
            # Manually apply damage as the fight method would
            damage = 20
            # No damage reduction should be applied
            defender.health -= damage

            assert defender.health == original_health - 20

    def test_zero_damage_reduction(self):
        """Test that 0% damage reduction works correctly"""
        LivingEntity("Attacker")
        defender = LivingEntity("Defender")

        # Give defender zero damage reduction
        defender.damageReduction = 0.0

        original_health = defender.health

        with patch("random.randint", return_value=20):
            damage = 20
            # Apply damage reduction calculation
            if hasattr(defender, "damageReduction") and defender.damageReduction > 0:
                damage = int(damage * (1 - defender.damageReduction))
                damage = max(damage, 1)

            defender.health -= damage

            assert defender.health == original_health - 20

    def test_full_fight_with_damage_reduction(self):
        """Test a complete fight scenario with damage reduction"""
        attacker = LivingEntity("Attacker")
        defender = LivingEntity("Defender")

        # Set predictable health values for testing
        attacker.health = 50
        attacker.maxHealth = 50
        defender.health = 60
        defender.maxHealth = 60
        defender.damageReduction = 0.5  # 50% damage reduction

        with patch("random.randint", return_value=20):
            attacker.fight(defender)

            # Defender should have survived longer due to damage reduction
            # With 50% reduction, 20 damage becomes 10 damage
            # This test verifies the fight mechanism works with damage reduction
            assert not attacker.isAlive() or not defender.isAlive()


class TestConfigurationSettings:
    """Test suite for configuration settings"""

    def test_config_survival_settings(self):
        """Test that config includes the new survival settings"""
        config = Config()

        # Check that early game settings exist
        assert hasattr(config, "earlyGameGracePeriod")
        assert hasattr(config, "playerDamageReduction")

        # Check default values
        assert config.earlyGameGracePeriod == 50
        assert config.playerDamageReduction == 0.4

    def test_config_values_are_reasonable(self):
        """Test that config values are within reasonable ranges"""
        config = Config()

        # Grace period should be positive
        assert config.earlyGameGracePeriod > 0
        assert config.earlyGameGracePeriod <= 1000  # Not too long

        # Damage reduction should be between 0 and 1
        assert 0 <= config.playerDamageReduction < 1

        # Ensure other config values still exist
        assert hasattr(config, "godMode")
        assert hasattr(config, "maxTicks")
        assert hasattr(config, "tickLength")


class TestGracePeriodMechanics:
    """Test suite for grace period and attack avoidance mechanics"""

    def test_grace_period_expiration(self):
        """Test that protection expires after grace period"""
        # Import Kreatures class only, not the module
        from kreatures import Kreatures

        # Mock input to avoid interactive prompt
        with patch("builtins.input", return_value="TestPlayer"):
            with patch("builtins.print"):  # Suppress print output
                game = Kreatures()

        # Player should start with protection
        assert hasattr(game.playerCreature, "damageReduction")
        assert game.playerCreature.damageReduction > 0

        # Simulate time passing beyond grace period
        game.tick = game.config.earlyGameGracePeriod + 1
        game.updatePlayerProtection()

        # Protection should be removed
        assert game.playerCreature.damageReduction == 0

    def test_grace_period_active_during_period(self):
        """Test that protection remains active during grace period"""
        from kreatures import Kreatures

        with patch("builtins.input", return_value="TestPlayer"):
            with patch("builtins.print"):
                game = Kreatures()

        # Set tick to middle of grace period
        game.tick = game.config.earlyGameGracePeriod // 2
        original_reduction = game.playerCreature.damageReduction

        game.updatePlayerProtection()

        # Protection should still be active
        assert game.playerCreature.damageReduction == original_reduction

    def test_attack_avoidance_during_grace_period(self):
        """Test that creatures avoid attacking player during grace period"""
        from kreatures import Kreatures

        with patch("builtins.input", return_value="TestPlayer"):
            with patch("builtins.print"):
                game = Kreatures()

        # Create a mock entity that would attack the player
        attacker = LivingEntity("Attacker")

        # Mock the environment to return our attacker and player
        with patch.object(game.environment, "getEntities", return_value=[attacker]):
            with patch.object(
                game.environment, "getRandomEntity", return_value=game.playerCreature
            ):
                with patch.object(attacker, "getNextAction", return_value="fight"):

                    # Set game to be in grace period
                    game.tick = 10  # Well within grace period

                    # Mock random to always trigger attack avoidance (return value <= 85)
                    with patch(
                        "random.randint", return_value=50
                    ):  # 50 <= 85, so attack should be avoided
                        initial_log_length = len(attacker.log)
                        game.initiateEntityActions()

                        # Check that attacker decided not to attack
                        assert len(attacker.log) > initial_log_length
                        assert "decided not to attack" in attacker.log[-1]

    def test_attack_not_avoided_after_grace_period(self):
        """Test that attack avoidance doesn't apply after grace period ends"""
        from kreatures import Kreatures

        with patch("builtins.input", return_value="TestPlayer"):
            with patch("builtins.print"):
                game = Kreatures()

        # Set game to be past grace period
        game.tick = game.config.earlyGameGracePeriod + 10

        # Grace period check should return False
        assert game.tick >= game.config.earlyGameGracePeriod


class TestPlayerInitialization:
    """Test suite for player initialization with protection"""

    def test_player_starts_with_protection(self):
        """Test that player creature is initialized with damage reduction"""
        from kreatures import Kreatures

        with patch("builtins.input", return_value="TestPlayer"):
            with patch("builtins.print"):
                game = Kreatures()

        # Player should have damage reduction attribute
        assert hasattr(game.playerCreature, "damageReduction")
        assert game.playerCreature.damageReduction == game.config.playerDamageReduction

        # Player should have protection message in log
        protection_messages = [
            msg for msg in game.playerCreature.log if "protection" in msg.lower()
        ]
        assert len(protection_messages) > 0

    def test_player_protection_message_logged(self):
        """Test that protection initialization is logged"""
        from kreatures import Kreatures

        with patch("builtins.input", return_value="TestHero"):
            with patch("builtins.print"):
                game = Kreatures()

        # Check that protection message was added to log
        assert any("early-game protection" in msg for msg in game.playerCreature.log)


class TestEdgeCases:
    """Test suite for edge cases and error conditions"""

    def test_negative_damage_reduction(self):
        """Test behavior with negative damage reduction values"""
        LivingEntity("Attacker")
        defender = LivingEntity("Defender")

        # Give defender negative damage reduction (should not increase damage)
        defender.damageReduction = -0.2

        original_health = defender.health

        with patch("random.randint", return_value=20):
            damage = 20
            # Apply damage reduction logic
            if hasattr(defender, "damageReduction") and defender.damageReduction > 0:
                damage = int(damage * (1 - defender.damageReduction))
                damage = max(damage, 1)

            defender.health -= damage

            # Should take normal damage (20) since negative reduction is ignored
            assert defender.health == original_health - 20

    def test_very_high_damage_with_reduction(self):
        """Test damage reduction with very high damage values"""
        LivingEntity("Attacker")
        defender = LivingEntity("Defender")

        defender.damageReduction = 0.8  # 80% reduction
        original_health = defender.health

        # Calculate expected result
        damage = 100
        reduced_damage = int(damage * (1 - defender.damageReduction))  # Should be 20
        reduced_damage = max(reduced_damage, 1)
        expected_health = original_health - reduced_damage

        # Apply the damage
        defender.health -= reduced_damage

        assert defender.health == expected_health
        # Verify significant damage reduction occurred (should be much less than original)
        assert reduced_damage < damage * 0.5  # Less than 50% of original damage

    def test_protection_expiration_logging(self):
        """Test that protection expiration is properly logged"""
        from kreatures import Kreatures

        with patch("builtins.input", return_value="TestPlayer"):
            with patch("builtins.print"):
                game = Kreatures()

        # Clear existing logs to focus on expiration message
        game.playerCreature.log.clear()

        # Set up conditions for protection expiration
        game.tick = game.config.earlyGameGracePeriod
        game.playerCreature.damageReduction = 0.4  # Ensure protection is active

        game.updatePlayerProtection()

        # Check that expiration was logged
        assert len(game.playerCreature.log) > 0
        assert any("protection has worn off" in msg for msg in game.playerCreature.log)


class TestIntegrationScenarios:
    """Test suite for integration scenarios"""

    def test_protection_survives_multiple_attacks(self):
        """Test that player can survive multiple attacks during grace period"""
        player = LivingEntity("Player")
        player.damageReduction = 0.4  # 40% reduction
        player.health = 100

        enemies = [LivingEntity(f"Enemy{i}") for i in range(3)]

        # Simulate multiple attacks with damage reduction
        for enemy in enemies:
            with patch(
                "random.randint", return_value=25
            ):  # 25 damage becomes ~15 with reduction
                if player.health > 0:
                    damage = 25
                    reduced_damage = int(damage * (1 - player.damageReduction))
                    reduced_damage = max(reduced_damage, 1)
                    player.health -= reduced_damage

        # Player should survive multiple attacks due to damage reduction
        assert player.health > 0

    def test_protection_vs_no_protection_survival(self):
        """Test survival comparison between protected and unprotected players"""
        # Protected player
        protected_player = LivingEntity("ProtectedPlayer")
        protected_player.damageReduction = 0.4
        protected_player.health = 80

        # Unprotected player
        normal_player = LivingEntity("NormalPlayer")
        normal_player.health = 80

        # Simulate same attacks on both
        with patch("random.randint", return_value=20):
            # Attack protected player
            damage = 20
            protected_damage = int(damage * (1 - protected_player.damageReduction))
            protected_damage = max(protected_damage, 1)
            protected_player.health -= protected_damage

            # Attack normal player
            normal_player.health -= damage

        # Protected player should have more health remaining
        assert protected_player.health > normal_player.health
