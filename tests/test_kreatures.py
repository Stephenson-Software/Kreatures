# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
"""Characterization tests for the Kreatures endgame paths.

These cover the four methods the player meets when their creature dies and
the simulation wraps up: getLivingChildren, continueAsChild, printSummary and
printStats. Every assertion here describes what the code does today, so a
failure means behavior changed rather than that the game is wrong.
"""
import sys
import os
import unittest
from unittest.mock import patch

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.livingEntity import LivingEntity


def printedLines(mock_print):
    """Flatten a mocked print's calls into the lines the player would see."""
    return [
        " ".join(str(arg) for arg in call.args) for call in mock_print.call_args_list
    ]


class KreaturesTestCase(unittest.TestCase):
    """Shared construction of a game whose interactive prompt is stubbed out."""

    @patch("builtins.input", return_value="TestPlayer")
    @patch("builtins.print")
    def setUp(self, mock_print, mock_input):
        from kreatures import Kreatures

        self.game = Kreatures()

    def addChildToWorld(self, name, parent=None):
        """Register a child of the player (or parent) that lives in the world."""
        if parent is None:
            parent = self.game.playerCreature
        child = LivingEntity(name)
        child.addParent(parent)
        parent.addChild(child)
        self.game.environment.addEntity(child)
        return child

    def addChildOutsideWorld(self, name):
        """Register a child of the player that is no longer in the world."""
        child = LivingEntity(name)
        child.addParent(self.game.playerCreature)
        self.game.playerCreature.addChild(child)
        return child


class TestGetLivingChildren(KreaturesTestCase):
    """Characterize which of an entity's children count as still alive."""

    def test_entity_with_no_children_has_no_living_children(self):
        self.assertEqual(self.game.getLivingChildren(self.game.playerCreature), [])

    def test_children_present_in_the_world_are_returned(self):
        first = self.addChildToWorld("Alison")
        second = self.addChildToWorld("Barry")

        self.assertEqual(
            self.game.getLivingChildren(self.game.playerCreature), [first, second]
        )

    def test_children_absent_from_the_world_are_filtered_out(self):
        living = self.addChildToWorld("Conrad")
        self.addChildOutsideWorld("Derrick")

        self.assertEqual(
            self.game.getLivingChildren(self.game.playerCreature), [living]
        )

    def test_membership_is_judged_by_the_world_not_by_health(self):
        """A child at zero health still counts, because only world membership
        is consulted. Deaths are reflected by removal from the world."""
        child = self.addChildToWorld("Eric")
        child.health = 0

        self.assertEqual(self.game.getLivingChildren(self.game.playerCreature), [child])

    def test_children_are_reported_in_the_order_they_were_added(self):
        first = self.addChildToWorld("Francis")
        second = self.addChildToWorld("Gary")
        third = self.addChildToWorld("Harry")

        self.assertEqual(
            self.game.getLivingChildren(self.game.playerCreature),
            [first, second, third],
        )

    def test_children_of_an_arbitrary_entity_are_reported(self):
        other = LivingEntity("Isabelle")
        self.game.environment.addEntity(other)
        child = self.addChildToWorld("Jasper", parent=other)

        self.assertEqual(self.game.getLivingChildren(other), [child])


class TestContinueAsChildDeclined(KreaturesTestCase):
    """Characterize the paths that leave the player's creature unchanged."""

    @patch("builtins.print")
    @patch("builtins.input")
    def test_no_living_children_returns_false_without_prompting(
        self, mock_input, mock_print
    ):
        self.addChildOutsideWorld("Alison")
        original = self.game.playerCreature

        self.assertFalse(self.game.continueAsChild())
        self.assertIs(self.game.playerCreature, original)
        mock_input.assert_not_called()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["n"])
    def test_declining_returns_false_and_keeps_the_dead_creature(
        self, mock_input, mock_print
    ):
        self.addChildToWorld("Barry")
        original = self.game.playerCreature
        self.game.running = False

        self.assertFalse(self.game.continueAsChild())
        self.assertIs(self.game.playerCreature, original)
        self.assertFalse(self.game.running)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["maybe"])
    def test_any_answer_other_than_yes_is_treated_as_a_decline(
        self, mock_input, mock_print
    ):
        self.addChildToWorld("Conrad")

        self.assertFalse(self.game.continueAsChild())


class TestContinueAsChildAccepted(KreaturesTestCase):
    """Characterize the succession itself once the player accepts."""

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["y"])
    def test_a_single_child_is_selected_without_a_further_prompt(
        self, mock_input, mock_print
    ):
        child = self.addChildToWorld("Derrick")
        self.game.running = False

        self.assertTrue(self.game.continueAsChild())
        self.assertIs(self.game.playerCreature, child)
        self.assertTrue(self.game.running)
        self.assertEqual(mock_input.call_count, 1)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["  YES  "])
    def test_the_answer_is_lowercased_and_stripped_before_matching(
        self, mock_input, mock_print
    ):
        child = self.addChildToWorld("Eric")

        self.assertTrue(self.game.continueAsChild())
        self.assertIs(self.game.playerCreature, child)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["y"])
    def test_the_new_player_is_moved_to_the_front_of_the_world(
        self, mock_input, mock_print
    ):
        child = self.addChildToWorld("Francis")

        self.game.continueAsChild()

        self.assertIs(self.game.environment.entities[0], child)
        self.assertEqual(self.game.environment.entities.count(child), 1)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["y", "2"])
    def test_a_numbered_choice_selects_from_several_children(
        self, mock_input, mock_print
    ):
        self.addChildToWorld("Gary")
        second = self.addChildToWorld("Harry")

        self.assertTrue(self.game.continueAsChild())
        self.assertIs(self.game.playerCreature, second)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["y", "2"])
    def test_the_children_are_listed_one_indexed_for_the_player(
        self, mock_input, mock_print
    ):
        self.addChildToWorld("Isabelle")
        self.addChildToWorld("Jasper")

        self.game.continueAsChild()
        lines = printedLines(mock_print)

        self.assertIn("1. Isabelle", lines)
        self.assertIn("2. Jasper", lines)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["y", "3", "0", "1"])
    def test_an_out_of_range_choice_is_rejected_and_re_prompted(
        self, mock_input, mock_print
    ):
        first = self.addChildToWorld("Alison")
        self.addChildToWorld("Barry")

        self.assertTrue(self.game.continueAsChild())
        self.assertIs(self.game.playerCreature, first)
        self.assertEqual(
            printedLines(mock_print).count("Invalid choice. Please try again."), 2
        )

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["y", "second", "2"])
    def test_a_non_numeric_choice_is_rejected_and_re_prompted(
        self, mock_input, mock_print
    ):
        self.addChildToWorld("Conrad")
        second = self.addChildToWorld("Derrick")

        self.assertTrue(self.game.continueAsChild())
        self.assertIs(self.game.playerCreature, second)
        self.assertIn("Please enter a number.", printedLines(mock_print))

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["y"])
    def test_only_living_children_are_offered(self, mock_input, mock_print):
        """With one child in the world and one outside it, the single-child
        path is taken — the count the player is told reflects the filter."""
        living = self.addChildToWorld("Eric")
        self.addChildOutsideWorld("Francis")

        self.assertTrue(self.game.continueAsChild())
        self.assertIs(self.game.playerCreature, living)
        self.assertEqual(mock_input.call_count, 1)
        self.assertTrue(
            any("has 1 living children" in line for line in printedLines(mock_print)),
            "the count announced to the player should reflect the filter",
        )


class TestPrintSummary(KreaturesTestCase):
    """Characterize the end-of-run summary the player is shown."""

    def summaryLines(self):
        with patch("builtins.print") as mock_print:
            self.game.printSummary()
        return printedLines(mock_print)

    def test_a_creature_that_fights_more_than_it_befriends_is_ferocious(self):
        self.game.playerCreature.chanceToFight = 70
        self.game.playerCreature.chanceToBefriend = 30

        self.assertIn("TestPlayer was ferocious.", self.summaryLines())

    def test_a_creature_that_befriends_more_than_it_fights_is_friendly(self):
        self.game.playerCreature.chanceToFight = 30
        self.game.playerCreature.chanceToBefriend = 70

        self.assertIn("TestPlayer was very friendly.", self.summaryLines())

    def test_equal_tendencies_are_reported_as_neutral(self):
        self.game.playerCreature.chanceToFight = 50
        self.game.playerCreature.chanceToBefriend = 50

        self.assertIn("TestPlayer was neutral.", self.summaryLines())

    def test_both_tendencies_are_reported_as_percentages(self):
        self.game.playerCreature.chanceToFight = 42
        self.game.playerCreature.chanceToBefriend = 58
        lines = self.summaryLines()

        self.assertIn("TestPlayer's chance to get into a fight was 42 percent.", lines)
        self.assertIn("TestPlayer's chance to be nice was 58 percent.", lines)

    def test_remaining_damage_reduction_is_reported_as_a_percentage(self):
        self.game.playerCreature.damageReduction = 0.4

        self.assertIn("TestPlayer still has 40% damage reduction.", self.summaryLines())

    def test_expired_damage_reduction_is_not_mentioned(self):
        self.game.playerCreature.damageReduction = 0

        for line in self.summaryLines():
            self.assertNotIn("damage reduction", line)

    def test_a_surviving_creature_reports_its_health(self):
        self.game.playerCreature.health = 37
        self.game.playerCreature.maxHealth = 100

        self.assertIn(
            "TestPlayer ended with 37 health (out of 100 max).", self.summaryLines()
        )

    def test_a_dead_creature_is_reported_as_having_died(self):
        self.game.playerCreature.health = 0
        lines = self.summaryLines()

        self.assertIn("TestPlayer died during the simulation.", lines)
        for line in lines:
            self.assertNotIn("ended with", line)

    def test_the_surviving_population_and_tick_count_are_reported(self):
        """The world's ten starter creatures are the whole population here:
        the player's creature only joins the world in placePlayerCreature,
        which the summary does not call."""
        self.game.tick = 17
        lines = self.summaryLines()

        self.assertIn("Kreatures still alive: 10", lines)
        self.assertIn("Simulation ran for 17 ticks.", lines)

    def test_average_tick_time_is_reported_only_once_ticks_were_timed(self):
        self.assertEqual(self.game.tickTimes, [])
        for line in self.summaryLines():
            self.assertNotIn("Average tick time", line)

        self.game.tickTimes = [0.01, 0.03]

        self.assertIn("Average tick time: 0.0200 seconds", self.summaryLines())

    def test_the_final_entity_limit_is_reported(self):
        self.game.config.maxEntities = 88

        self.assertIn(
            "Final max entities limit: 88 (started at 50)", self.summaryLines()
        )


class TestPrintStats(KreaturesTestCase):
    """Characterize the stat counters reported for the player's creature."""

    def test_the_three_counters_are_reported(self):
        self.game.playerCreature.stats.numFriendshipsForged = 3
        self.game.playerCreature.stats.numOffspring = 2
        self.game.playerCreature.stats.numCreaturesEaten = 1

        with patch("builtins.print") as mock_print:
            self.game.printStats()
        lines = printedLines(mock_print)

        self.assertEqual(
            lines,
            [
                "=== Stats ===",
                "Friendships forged: 3",
                "Babies made: 2",
                "Creatures Eaten: 1",
            ],
        )

    def test_a_fresh_creature_reports_zeroes(self):
        with patch("builtins.print") as mock_print:
            self.game.printStats()
        lines = printedLines(mock_print)

        self.assertIn("Friendships forged: 0", lines)
        self.assertIn("Babies made: 0", lines)
        self.assertIn("Creatures Eaten: 0", lines)

    def test_the_stats_reported_are_the_current_player_creature_s(self):
        """After a succession the counters follow the new player creature."""
        child = self.addChildToWorld("Gary")
        child.stats.numOffspring = 9
        with patch("builtins.print"), patch("builtins.input", side_effect=["y"]):
            self.game.continueAsChild()

        with patch("builtins.print") as mock_print:
            self.game.printStats()

        self.assertIn("Babies made: 9", printedLines(mock_print))


if __name__ == "__main__":
    unittest.main()
