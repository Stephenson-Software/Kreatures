# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
"""Characterization tests for Kreatures.initiateEntityActions.

Each tick every creature in the world picks a random target and acts on the
decision getNextAction returns. These tests pin down what each of the four
decisions does to the actor, the target and the world, plus the rules that
keep a creature from acting at all. Decisions and targets are scripted so
every branch is exercised deterministically. Every assertion describes what
the code does today, so a failure means behavior changed rather than that
the game is wrong.
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.livingEntity import LivingEntity


def scriptedEntity(name, decision=None, health=100):
    """A LivingEntity with even tendencies, fixed health and, if given, a
    getNextAction that always returns decision."""
    entity = LivingEntity(name)
    entity.chanceToFight = 50
    entity.chanceToBefriend = 50
    entity.health = health
    entity.maxHealth = health
    if decision is not None:
        entity.getNextAction = Mock(return_value=decision)
    return entity


class EntityActionsTestCase(unittest.TestCase):
    """Shared construction of a game whose world holds only scripted
    creatures and whose target selection is scripted too."""

    @patch("builtins.input", return_value="TestPlayer")
    @patch("builtins.print")
    def setUp(self, mock_print, mock_input):
        from kreatures import Kreatures

        self.game = Kreatures()
        self.game.environment.entities = []

    def populate(self, *entities):
        for entity in entities:
            self.game.environment.addEntity(entity)

    def scriptTargets(self, *targets):
        """Hand out targets in order, one per creature that takes a turn."""
        self.game.environment.getRandomEntity = Mock(side_effect=list(targets))

    def runTick(self):
        with patch("builtins.print"):
            self.game.initiateEntityActions()


class TestSkippedTurns(EntityActionsTestCase):
    """Characterize when a creature does not act at all."""

    def test_a_creature_that_draws_itself_does_not_act(self):
        actor = scriptedEntity("Alison", "befriend")
        self.populate(actor)
        self.scriptTargets(actor)

        self.runTick()

        actor.getNextAction.assert_not_called()

    def test_a_creature_that_draws_no_target_does_not_act(self):
        actor = scriptedEntity("Alison", "befriend")
        self.populate(actor)
        self.scriptTargets(None)

        self.runTick()

        actor.getNextAction.assert_not_called()

    def test_every_creature_draws_its_own_target(self):
        first = scriptedEntity("Alison", "nothing")
        second = scriptedEntity("Barry", "nothing")
        self.populate(first, second)
        self.scriptTargets(second, first)

        self.runTick()

        first.getNextAction.assert_called_once_with(second)
        second.getNextAction.assert_called_once_with(first)


class TestNothingDecision(EntityActionsTestCase):
    """Characterize the "nothing" decision: an argument, and nothing else."""

    def setUp(self):
        super().setUp()
        self.actor = scriptedEntity("Alison", "nothing")
        self.target = scriptedEntity("Barry")
        self.populate(self.actor, self.target)
        self.scriptTargets(self.target, self.target)

    def test_the_actor_logs_an_argument_with_the_target(self):
        self.runTick()

        self.assertEqual(self.actor.log[-1], "Alison had an argument with Barry!")

    def test_the_target_is_not_told_about_the_argument(self):
        before = list(self.target.log)

        self.runTick()

        self.assertEqual(list(self.target.log), before)

    def test_no_tendency_changes(self):
        self.runTick()

        self.assertEqual(
            (self.actor.chanceToFight, self.actor.chanceToBefriend), (50, 50)
        )


class TestBefriendDecision(EntityActionsTestCase):
    """Characterize the "befriend" decision."""

    def setUp(self):
        super().setUp()
        self.actor = scriptedEntity("Alison", "befriend")
        self.target = scriptedEntity("Barry")
        self.populate(self.actor, self.target)
        self.scriptTargets(self.target, self.target)

    def test_the_two_creatures_become_mutual_friends(self):
        self.runTick()

        self.assertEqual(self.actor.friends, [self.target])
        self.assertEqual(self.target.friends, [self.actor])

    def test_only_the_actor_becomes_friendlier(self):
        self.runTick()

        self.assertEqual(
            (self.actor.chanceToFight, self.actor.chanceToBefriend), (49, 51)
        )
        self.assertEqual(
            (self.target.chanceToFight, self.target.chanceToBefriend), (50, 50)
        )

    def test_no_creature_enters_or_leaves_the_world(self):
        self.runTick()

        self.assertEqual(self.game.environment.entities, [self.actor, self.target])


class TestLoveDecision(EntityActionsTestCase):
    """Characterize the "love" decision: two friends have a child."""

    def setUp(self):
        super().setUp()
        self.actor = scriptedEntity("Alison", "love")
        self.target = scriptedEntity("Barry")
        self.populate(self.actor, self.target)

    def test_a_child_of_both_creatures_joins_the_world(self):
        self.scriptTargets(self.target, self.target, None)

        self.runTick()

        self.assertEqual(len(self.game.environment.entities), 3)
        child = self.game.environment.entities[2]
        self.assertEqual(child.parents, [self.actor, self.target])
        self.assertEqual(self.actor.children, [child])
        self.assertEqual(self.target.children, [child])

    def test_both_parents_count_the_offspring(self):
        self.scriptTargets(self.target, self.target, None)

        self.runTick()

        self.assertEqual(self.actor.stats.numOffspring, 1)
        self.assertEqual(self.target.stats.numOffspring, 1)

    def test_only_the_actor_becomes_friendlier(self):
        self.scriptTargets(self.target, self.target, None)

        self.runTick()

        self.assertEqual(
            (self.actor.chanceToFight, self.actor.chanceToBefriend), (49, 51)
        )
        self.assertEqual(
            (self.target.chanceToFight, self.target.chanceToBefriend), (50, 50)
        )

    def test_a_child_born_this_tick_takes_a_turn_in_the_same_tick(self):
        """The child is appended to the very list being iterated, so the loop
        reaches it before the tick ends and it draws a target of its own."""
        self.scriptTargets(self.target, self.target, None)

        self.runTick()

        self.assertEqual(self.game.environment.getRandomEntity.call_count, 3)

    def test_a_crowded_world_gets_no_child_but_the_offspring_still_count(self):
        """createChildEntity refuses the child, but reproduce has already
        credited both parents with it by then."""
        self.game.canCreateNewEntity = Mock(return_value=False)
        self.scriptTargets(self.target, self.target)

        self.runTick()

        self.assertEqual(self.game.environment.entities, [self.actor, self.target])
        self.assertEqual(self.actor.stats.numOffspring, 1)
        self.assertEqual(self.target.stats.numOffspring, 1)
        crowded = (
            "Alison and Barry tried to have a child, but the world is too crowded!"
        )
        self.assertEqual(self.actor.log[-1], crowded)
        self.assertEqual(self.target.log[-1], crowded)


class TestFightDecision(EntityActionsTestCase):
    """Characterize the "fight" decision against another creature."""

    def test_the_actor_becomes_more_ferocious(self):
        actor = scriptedEntity("Alison", "fight")
        target = scriptedEntity("Barry", health=1)
        self.populate(actor, target)
        self.scriptTargets(target, target)

        self.runTick()

        self.assertEqual((actor.chanceToFight, actor.chanceToBefriend), (51, 49))

    def test_a_target_eaten_in_the_fight_leaves_the_world(self):
        actor = scriptedEntity("Alison", "fight")
        target = scriptedEntity("Barry", health=1)
        self.populate(actor, target)
        self.scriptTargets(target, target)

        self.runTick()

        self.assertEqual(self.game.environment.entities, [actor])
        self.assertEqual(actor.stats.numCreaturesEaten, 1)

    def test_an_actor_eaten_in_the_fight_it_started_leaves_the_world(self):
        actor = scriptedEntity("Alison", "fight", health=1)
        target = scriptedEntity("Barry", health=1000)
        self.populate(actor, target)
        self.scriptTargets(target, target)

        self.runTick()

        self.assertEqual(self.game.environment.entities, [target])
        self.assertEqual(target.stats.numCreaturesEaten, 1)

    def test_a_creature_eaten_earlier_in_the_tick_still_takes_its_turn(self):
        """Deaths are only applied once every creature has acted, so a
        creature eaten earlier in the same tick still acts on its own turn
        — here it forges a friendship — before it is removed."""
        eater = scriptedEntity("Alison", "fight")
        eaten = scriptedEntity("Barry", "befriend", health=1)
        bystander = scriptedEntity("Conrad", "nothing")
        self.populate(eater, eaten, bystander)
        self.scriptTargets(eaten, bystander, bystander)

        self.runTick()

        eaten.getNextAction.assert_called_once_with(bystander)
        self.assertEqual(bystander.friends, [eaten])
        self.assertEqual(self.game.environment.entities, [eater, bystander])


class TestFightingThePlayer(EntityActionsTestCase):
    """Characterize the extra rules that apply when the player is attacked."""

    def setUp(self):
        super().setUp()
        self.attacker = scriptedEntity("Alison", "fight")
        self.player = self.game.playerCreature
        self.player.health = 1
        self.populate(self.attacker)
        self.scriptTargets(self.player)

    def test_god_mode_calls_the_attack_off_silently(self):
        self.game.config.godMode = True
        log_before = list(self.attacker.log)

        self.runTick()

        self.assertTrue(self.player.isAlive())
        self.assertEqual(list(self.attacker.log), log_before)
        self.assertEqual(
            (self.attacker.chanceToFight, self.attacker.chanceToBefriend), (50, 50)
        )

    def test_a_grace_period_roll_above_85_lets_the_attack_through(self):
        self.game.tick = 0

        with patch("random.randint", return_value=86):
            self.runTick()

        self.assertFalse(self.player.isAlive())

    def test_the_grace_period_roll_is_not_made_once_the_period_is_over(self):
        """A roll of 50 would call the attack off during the grace period."""
        self.game.tick = self.game.config.earlyGameGracePeriod

        with patch("random.randint", return_value=50):
            self.runTick()

        self.assertFalse(self.player.isAlive())
        self.assertEqual(
            (self.attacker.chanceToFight, self.attacker.chanceToBefriend), (51, 49)
        )


if __name__ == "__main__":
    unittest.main()
