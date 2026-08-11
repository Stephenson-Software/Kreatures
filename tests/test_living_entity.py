# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.livingEntity import LivingEntity, DEFAULT_LOG_MAX_SIZE
from flags.flags import Flags
from stats.stats import Stats


class TestLivingEntityInitialization(unittest.TestCase):
    """Characterize the state a freshly constructed entity starts with."""

    def test_starting_attributes_are_within_documented_ranges(self):
        entity = LivingEntity("Alison")

        self.assertEqual(entity.name, "Alison")
        self.assertTrue(45 <= entity.chanceToFight <= 55)
        self.assertTrue(80 <= entity.health <= 120)

    def test_chance_to_befriend_is_the_complement_of_chance_to_fight(self):
        entity = LivingEntity("Barry")

        self.assertEqual(entity.chanceToBefriend, 100 - entity.chanceToFight)

    def test_max_health_starts_equal_to_health(self):
        entity = LivingEntity("Conrad")

        self.assertEqual(entity.maxHealth, entity.health)

    def test_relationship_collections_start_empty(self):
        entity = LivingEntity("Derrick")

        self.assertEqual(entity.friends, [])
        self.assertEqual(entity.parents, [])
        self.assertEqual(entity.children, [])

    def test_stats_and_flags_are_own_instances(self):
        first = LivingEntity("Eric")
        second = LivingEntity("Francis")

        self.assertIsInstance(first.stats, Stats)
        self.assertIsInstance(first.flags, Flags)
        self.assertIsNot(first.stats, second.stats)
        self.assertIsNot(first.flags, second.flags)

    def test_log_starts_with_a_creation_entry(self):
        entity = LivingEntity("Gary")

        self.assertEqual(len(entity.log), 1)
        self.assertEqual(entity.log[0], "Gary was created.")

    def test_log_cap_defaults_to_the_shared_constant(self):
        entity = LivingEntity("Harry")

        self.assertEqual(entity.log.maxlen, DEFAULT_LOG_MAX_SIZE)

    def test_log_cap_honours_an_explicit_max_log_size(self):
        entity = LivingEntity("Isabelle", maxLogSize=3)

        self.assertEqual(entity.log.maxlen, 3)


class TestRollForMovement(unittest.TestCase):
    """rollForMovement is a flat 1-in-10 roll."""

    def test_returns_true_on_a_roll_of_one(self):
        entity = LivingEntity("Jasper")

        with patch("entity.livingEntity.random.randint", return_value=1):
            self.assertTrue(entity.rollForMovement())

    def test_returns_false_on_any_other_roll(self):
        entity = LivingEntity("Jasper")

        for roll in range(2, 11):
            with patch("entity.livingEntity.random.randint", return_value=roll):
                self.assertFalse(entity.rollForMovement())


class TestGetNextAction(unittest.TestCase):
    """getNextAction picks between fighting, befriending, loving and nothing."""

    def setUp(self):
        self.entity = LivingEntity("Actor")
        self.entity.chanceToFight = 50
        self.target = LivingEntity("Target")

    def test_returns_fight_for_a_stranger_when_the_roll_is_low(self):
        with patch("entity.livingEntity.random.randint", return_value=10):
            self.assertEqual(self.entity.getNextAction(self.target), "fight")

    def test_returns_befriend_for_a_stranger_when_the_roll_is_high(self):
        with patch("entity.livingEntity.random.randint", return_value=90):
            self.assertEqual(self.entity.getNextAction(self.target), "befriend")

    def test_returns_nothing_for_a_friend_when_the_roll_is_low(self):
        self.entity.friends.append(self.target)

        with patch("entity.livingEntity.random.randint", return_value=10):
            self.assertEqual(self.entity.getNextAction(self.target), "nothing")

    def test_returns_love_for_a_friend_when_the_roll_is_high(self):
        self.entity.friends.append(self.target)

        with patch("entity.livingEntity.random.randint", return_value=90):
            self.assertEqual(self.entity.getNextAction(self.target), "love")

    def test_a_roll_equal_to_chance_to_fight_takes_the_fight_branch(self):
        with patch("entity.livingEntity.random.randint", return_value=50):
            self.assertEqual(self.entity.getNextAction(self.target), "fight")

    def test_a_roll_one_above_chance_to_fight_takes_the_befriend_branch(self):
        with patch("entity.livingEntity.random.randint", return_value=51):
            self.assertEqual(self.entity.getNextAction(self.target), "befriend")

    def test_friendship_is_matched_by_name_not_identity(self):
        """A distinct creature that happens to share a friend's name is
        currently treated as that friend. This locks in today's behavior; see
        the discussion on issue #38 about whether identity matching is
        intended instead."""
        self.entity.friends.append(self.target)
        namesake = LivingEntity("Target")

        self.assertIsNot(namesake, self.target)
        with patch("entity.livingEntity.random.randint", return_value=90):
            self.assertEqual(self.entity.getNextAction(namesake), "love")

    def test_declining_to_fight_a_friend_does_not_count_as_an_action(self):
        """The "nothing" branch returns before numActionsTaken is touched,
        unlike every other branch."""
        self.entity.friends.append(self.target)

        with patch("entity.livingEntity.random.randint", return_value=10):
            self.entity.getNextAction(self.target)

        self.assertEqual(self.entity.stats.numActionsTaken, 0)

    def test_fight_befriend_and_love_each_count_as_an_action(self):
        for roll, friend in ((10, False), (90, False), (90, True)):
            entity = LivingEntity("Actor")
            entity.chanceToFight = 50
            target = LivingEntity("Target")
            if friend:
                entity.friends.append(target)

            with patch("entity.livingEntity.random.randint", return_value=roll):
                entity.getNextAction(target)

            self.assertEqual(entity.stats.numActionsTaken, 1)

    def test_the_decision_roll_is_recorded_on_the_entity(self):
        with patch("entity.livingEntity.random.randint", return_value=37):
            self.entity.getNextAction(self.target)

        self.assertEqual(self.entity.decision, 37)


class TestReproduce(unittest.TestCase):
    """reproduce credits both parents and hands them back to the caller."""

    def setUp(self):
        self.mother = LivingEntity("Alison")
        self.father = LivingEntity("Barry")

    def test_returns_both_parents_in_call_order(self):
        self.assertEqual(self.mother.reproduce(self.father), (self.mother, self.father))

    def test_increments_offspring_count_for_both_parents(self):
        self.mother.reproduce(self.father)

        self.assertEqual(self.mother.stats.numOffspring, 1)
        self.assertEqual(self.father.stats.numOffspring, 1)

    def test_logs_the_event_from_each_parents_perspective(self):
        self.mother.reproduce(self.father)

        self.assertEqual(self.mother.log[-1], "Alison made a baby with Barry!")
        self.assertEqual(self.father.log[-1], "Barry made a baby with Alison!")


class TestFight(unittest.TestCase):
    """fight runs to the death, with the caller striking first each round."""

    def setUp(self):
        self.attacker = LivingEntity("Attacker")
        self.defender = LivingEntity("Defender")

    def test_attacker_strikes_first_and_can_win_before_being_hit(self):
        self.attacker.health = 100
        self.defender.health = 20

        with patch("entity.livingEntity.random.randint", return_value=20):
            self.attacker.fight(self.defender)

        self.assertEqual(self.attacker.health, 100)
        self.assertLessEqual(self.defender.health, 0)

    def test_the_winner_is_credited_with_eating_the_loser(self):
        self.attacker.health = 100
        self.defender.health = 20

        with patch("entity.livingEntity.random.randint", return_value=20):
            self.attacker.fight(self.defender)

        self.assertEqual(self.attacker.stats.numCreaturesEaten, 1)
        self.assertEqual(self.defender.stats.numCreaturesEaten, 0)
        self.assertEqual(self.attacker.log[-1], "Attacker fought and ate Defender!")
        self.assertEqual(self.defender.log[-1], "Defender was eaten by Attacker!")

    def test_the_defender_can_win_on_the_counter_attack(self):
        self.attacker.health = 20
        self.defender.health = 100

        with patch("entity.livingEntity.random.randint", return_value=20):
            self.attacker.fight(self.defender)

        self.assertLessEqual(self.attacker.health, 0)
        self.assertEqual(self.defender.stats.numCreaturesEaten, 1)
        self.assertEqual(self.defender.log[-1], "Defender fought and ate Attacker!")
        self.assertEqual(self.attacker.log[-1], "Attacker was eaten by Defender!")

    def test_a_survived_blow_is_logged_from_both_sides(self):
        self.attacker.health = 100
        self.defender.health = 60

        with patch("entity.livingEntity.random.randint", return_value=20):
            self.attacker.fight(self.defender)

        self.assertIn(
            "Attacker fought Defender and dealt 20 damage!", list(self.attacker.log)
        )
        self.assertIn(
            "Defender took 20 damage from Attacker! Health: 40", list(self.defender.log)
        )

    def test_damage_reduction_scales_incoming_damage(self):
        self.attacker.health = 100
        self.defender.health = 60
        self.defender.damageReduction = 0.5

        with patch("entity.livingEntity.random.randint", return_value=20):
            self.attacker.fight(self.defender)

        self.assertIn(
            "Defender took 10 damage from Attacker! Health: 50", list(self.defender.log)
        )

    def test_damage_reduction_applies_to_the_counter_attack_too(self):
        self.attacker.health = 100
        self.attacker.damageReduction = 0.5
        self.defender.health = 100

        with patch("entity.livingEntity.random.randint", return_value=20):
            self.attacker.fight(self.defender)

        self.assertIn(
            "Attacker took 10 damage from Defender! Health: 90", list(self.attacker.log)
        )

    def test_damage_reduction_never_reduces_a_blow_below_one(self):
        self.attacker.health = 1000
        self.defender.health = 3
        self.defender.damageReduction = 1.0

        with patch("entity.livingEntity.random.randint", return_value=20):
            self.attacker.fight(self.defender)

        self.assertLessEqual(self.defender.health, 0)
        self.assertIn(
            "Defender took 1 damage from Attacker! Health: 2", list(self.defender.log)
        )

    def test_the_fight_always_ends_with_exactly_one_survivor(self):
        self.attacker.health = 100
        self.defender.health = 100

        self.attacker.fight(self.defender)

        survivors = [e for e in (self.attacker, self.defender) if e.isAlive()]
        self.assertEqual(len(survivors), 1)


class TestBefriend(unittest.TestCase):
    """befriend is bidirectional: both entities gain the friendship."""

    def setUp(self):
        self.entity = LivingEntity("Alison")
        self.other = LivingEntity("Barry")

    def test_each_entity_is_added_to_the_others_friend_list(self):
        self.entity.befriend(self.other)

        self.assertIn(self.other, self.entity.friends)
        self.assertIn(self.entity, self.other.friends)

    def test_both_friendship_counters_are_incremented(self):
        self.entity.befriend(self.other)

        self.assertEqual(self.entity.stats.numFriendshipsForged, 1)
        self.assertEqual(self.other.stats.numFriendshipsForged, 1)

    def test_logs_the_event_from_each_perspective(self):
        self.entity.befriend(self.other)

        self.assertEqual(self.entity.log[-1], "Alison made friends with Barry!")
        self.assertEqual(self.other.log[-1], "Barry made friends with Alison!")

    def test_befriending_the_same_entity_twice_duplicates_the_entry(self):
        """Nothing guards against a repeat friendship today."""
        self.entity.befriend(self.other)
        self.entity.befriend(self.other)

        self.assertEqual(self.entity.friends.count(self.other), 2)
        self.assertEqual(self.entity.stats.numFriendshipsForged, 2)


class TestBehaviouralChanceAdjustments(unittest.TestCase):
    """The four chance adjusters step by flags.increaseAmount and clamp."""

    def setUp(self):
        self.entity = LivingEntity("Alison")

    def test_increase_chance_to_fight_steps_by_the_flag_amount(self):
        self.entity.chanceToFight = 50

        self.entity.increaseChanceToFight()

        self.assertEqual(
            self.entity.chanceToFight, 50 + self.entity.flags.increaseAmount
        )

    def test_decrease_chance_to_fight_steps_by_the_flag_amount(self):
        self.entity.chanceToFight = 50

        self.entity.decreaseChanceToFight()

        self.assertEqual(
            self.entity.chanceToFight, 50 - self.entity.flags.increaseAmount
        )

    def test_increase_chance_to_befriend_steps_by_the_flag_amount(self):
        self.entity.chanceToBefriend = 50

        self.entity.increaseChanceToBefriend()

        self.assertEqual(
            self.entity.chanceToBefriend, 50 + self.entity.flags.increaseAmount
        )

    def test_decrease_chance_to_befriend_steps_by_the_flag_amount(self):
        self.entity.chanceToBefriend = 50

        self.entity.decreaseChanceToBefriend()

        self.assertEqual(
            self.entity.chanceToBefriend, 50 - self.entity.flags.increaseAmount
        )

    def test_chance_to_fight_is_clamped_to_one_hundred(self):
        self.entity.chanceToFight = 100

        self.entity.increaseChanceToFight()

        self.assertEqual(self.entity.chanceToFight, 100)

    def test_chance_to_fight_is_clamped_to_zero(self):
        self.entity.chanceToFight = 0

        self.entity.decreaseChanceToFight()

        self.assertEqual(self.entity.chanceToFight, 0)

    def test_chance_to_befriend_is_clamped_to_one_hundred(self):
        self.entity.chanceToBefriend = 100

        self.entity.increaseChanceToBefriend()

        self.assertEqual(self.entity.chanceToBefriend, 100)

    def test_chance_to_befriend_is_clamped_to_zero(self):
        self.entity.chanceToBefriend = 0

        self.entity.decreaseChanceToBefriend()

        self.assertEqual(self.entity.chanceToBefriend, 0)

    def test_adjusting_one_chance_leaves_the_other_untouched(self):
        """The two values are independent; nothing keeps them summing to 100."""
        self.entity.chanceToFight = 50
        self.entity.chanceToBefriend = 50

        self.entity.increaseChanceToFight()

        self.assertEqual(self.entity.chanceToBefriend, 50)


class TestRelationshipTracking(unittest.TestCase):
    """addChild and addParent are one-directional appends."""

    def setUp(self):
        self.parent = LivingEntity("Alison")
        self.child = LivingEntity("Cleo")

    def test_add_child_appends_to_children(self):
        self.parent.addChild(self.child)

        self.assertEqual(self.parent.children, [self.child])

    def test_add_parent_appends_to_parents(self):
        self.child.addParent(self.parent)

        self.assertEqual(self.child.parents, [self.parent])

    def test_add_child_does_not_set_the_reverse_link(self):
        """Callers are responsible for pairing addChild with addParent."""
        self.parent.addChild(self.child)

        self.assertEqual(self.child.parents, [])


class TestIsAlive(unittest.TestCase):
    """isAlive is a strict health > 0 check."""

    def setUp(self):
        self.entity = LivingEntity("Alison")

    def test_positive_health_is_alive(self):
        self.entity.health = 1

        self.assertTrue(self.entity.isAlive())

    def test_zero_health_is_not_alive(self):
        self.entity.health = 0

        self.assertFalse(self.entity.isAlive())

    def test_negative_health_is_not_alive(self):
        self.entity.health = -5

        self.assertFalse(self.entity.isAlive())


class TestRegenerateHealth(unittest.TestCase):
    """Regeneration is a 30% per-tick chance to recover 1-3 health."""

    def setUp(self):
        self.entity = LivingEntity("Alison")
        self.entity.maxHealth = 100
        self.entity.health = 90

    def test_a_successful_roll_restores_the_rolled_amount(self):
        with patch("entity.livingEntity.random.randint", side_effect=[3, 2]):
            self.entity.regenerateHealth()

        self.assertEqual(self.entity.health, 92)

    def test_a_failed_roll_leaves_health_untouched(self):
        with patch("entity.livingEntity.random.randint", side_effect=[4]):
            self.entity.regenerateHealth()

        self.assertEqual(self.entity.health, 90)

    def test_health_at_maximum_skips_the_roll_entirely(self):
        self.entity.health = 100

        with patch("entity.livingEntity.random.randint") as randint:
            self.entity.regenerateHealth()

        randint.assert_not_called()
        self.assertEqual(self.entity.health, 100)

    def test_regeneration_never_overshoots_maximum_health(self):
        self.entity.health = 99

        with patch("entity.livingEntity.random.randint", side_effect=[1, 3]):
            self.entity.regenerateHealth()

        self.assertEqual(self.entity.health, 100)

    def test_a_regeneration_of_two_or_more_is_logged(self):
        with patch("entity.livingEntity.random.randint", side_effect=[1, 2]):
            self.entity.regenerateHealth()

        self.assertEqual(
            self.entity.log[-1], "Alison regenerated 2 health! Health: 92/100"
        )

    def test_a_regeneration_of_one_is_not_logged(self):
        """Single-point ticks are deliberately silent to avoid log spam."""
        entriesBefore = len(self.entity.log)

        with patch("entity.livingEntity.random.randint", side_effect=[1, 1]):
            self.entity.regenerateHealth()

        self.assertEqual(self.entity.health, 91)
        self.assertEqual(len(self.entity.log), entriesBefore)

    def test_a_dead_entity_can_still_regenerate(self):
        """Regeneration does not check isAlive(); the caller is expected to."""
        self.entity.health = 0

        with patch("entity.livingEntity.random.randint", side_effect=[1, 3]):
            self.entity.regenerateHealth()

        self.assertEqual(self.entity.health, 3)


if __name__ == "__main__":
    unittest.main()
