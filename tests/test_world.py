# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.livingEntity import LivingEntity, DEFAULT_LOG_MAX_SIZE
from world.world import World

STARTER_NAMES = [
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


def emptyWorld():
    """A World with its ten starter creatures cleared out, so a test can
    populate it with exactly the entities it is about."""
    world = World()
    world.entities = []
    return world


def entityWithHealth(name, health, numChildren=0):
    """A LivingEntity with deterministic health and a given number of
    children, the two keys cullWeakestEntities sorts on."""
    entity = LivingEntity(name)
    entity.health = health
    entity.maxHealth = health
    for i in range(numChildren):
        entity.addChild(LivingEntity("%s-child-%d" % (name, i)))
    return entity


class TestWorldInitialization(unittest.TestCase):
    """Characterize the ten-creature world every game starts from."""

    def test_starts_with_ten_starter_creatures_in_alphabetical_order(self):
        world = World()

        self.assertEqual(world.getNumEntities(), 10)
        self.assertEqual([e.name for e in world.getEntities()], STARTER_NAMES)

    def test_every_starter_is_a_living_entity(self):
        world = World()

        for entity in world.getEntities():
            self.assertIsInstance(entity, LivingEntity)

    def test_starter_entities_are_the_same_objects_as_the_world_entities(self):
        world = World()

        self.assertEqual(world.starterEntities, world.entities)
        for starter, entity in zip(world.starterEntities, world.entities):
            self.assertIs(starter, entity)

    def test_starter_entities_is_a_separate_list_from_entities(self):
        """starterEntities is a record of the initial population, not an
        alias of the live list, so later additions do not appear in it."""
        world = World()

        world.addEntity(LivingEntity("Newcomer"))

        self.assertIsNot(world.starterEntities, world.entities)
        self.assertEqual(len(world.starterEntities), 10)
        self.assertEqual(world.getNumEntities(), 11)

    def test_each_starter_is_also_reachable_as_a_named_attribute(self):
        world = World()

        for index, name in enumerate(STARTER_NAMES):
            self.assertIs(getattr(world, name), world.entities[index])

    def test_starters_use_the_default_log_cap(self):
        world = World()

        for entity in world.getEntities():
            self.assertEqual(entity.log.maxlen, DEFAULT_LOG_MAX_SIZE)

    def test_starters_honour_an_explicit_max_log_size(self):
        world = World(maxLogSize=7)

        for entity in world.getEntities():
            self.assertEqual(entity.log.maxlen, 7)

    def test_two_worlds_do_not_share_starter_creatures(self):
        first = World()
        second = World()

        self.assertIsNot(first.Alison, second.Alison)
        self.assertIsNot(first.entities, second.entities)


class TestAddAndRemoveEntity(unittest.TestCase):
    """addEntity appends; removeEntity removes one entity by identity."""

    def test_add_entity_appends_to_the_end(self):
        world = World()
        newcomer = LivingEntity("Newcomer")

        world.addEntity(newcomer)

        self.assertIs(world.getEntities()[-1], newcomer)
        self.assertEqual(world.getNumEntities(), 11)

    def test_add_entity_does_not_deduplicate(self):
        """Nothing guards against adding the same entity twice."""
        world = emptyWorld()
        entity = LivingEntity("Twice")

        world.addEntity(entity)
        world.addEntity(entity)

        self.assertEqual(world.getEntities(), [entity, entity])

    def test_remove_entity_removes_only_that_entity(self):
        world = World()
        conrad = world.Conrad

        world.removeEntity(conrad)

        self.assertNotIn(conrad, world.getEntities())
        self.assertEqual(world.getNumEntities(), 9)
        self.assertEqual(
            [e.name for e in world.getEntities()],
            [name for name in STARTER_NAMES if name != "Conrad"],
        )

    def test_remove_entity_matches_by_identity_not_by_name(self):
        """A different entity carrying a starter's name is not a match."""
        world = World()
        impostor = LivingEntity("Alison")

        with self.assertRaises(ValueError):
            world.removeEntity(impostor)

        self.assertEqual(world.getNumEntities(), 10)

    def test_remove_entity_raises_when_the_entity_is_absent(self):
        world = World()

        with self.assertRaises(ValueError):
            world.removeEntity(LivingEntity("Stranger"))

    def test_get_num_entities_tracks_the_live_population(self):
        world = emptyWorld()
        self.assertEqual(world.getNumEntities(), 0)

        first = LivingEntity("First")
        second = LivingEntity("Second")
        world.addEntity(first)
        world.addEntity(second)
        self.assertEqual(world.getNumEntities(), 2)

        world.removeEntity(first)
        self.assertEqual(world.getNumEntities(), 1)

    def test_get_entities_returns_the_live_list(self):
        """Callers receive the list itself, not a copy."""
        world = World()

        self.assertIs(world.getEntities(), world.entities)


class TestRemoveEntities(unittest.TestCase):
    """removeEntities drops a batch in one pass, tolerating absentees."""

    def test_removes_every_listed_entity_and_preserves_order(self):
        world = World()
        barry, eric, jasper = world.Barry, world.Eric, world.Jasper

        world.removeEntities([jasper, barry, eric])

        self.assertEqual(
            [e.name for e in world.getEntities()],
            [n for n in STARTER_NAMES if n not in ("Barry", "Eric", "Jasper")],
        )

    def test_ignores_entities_that_are_not_in_the_world(self):
        """Unlike removeEntity, an absent entity is silently skipped."""
        world = World()
        stranger = LivingEntity("Stranger")

        world.removeEntities([stranger, world.Gary])

        self.assertEqual(world.getNumEntities(), 9)
        self.assertNotIn(world.Gary, world.getEntities())

    def test_duplicates_in_the_batch_are_harmless(self):
        world = World()

        world.removeEntities([world.Harry, world.Harry])

        self.assertEqual(world.getNumEntities(), 9)
        self.assertNotIn(world.Harry, world.getEntities())

    def test_empty_batch_leaves_the_world_untouched(self):
        world = World()
        before = world.entities

        world.removeEntities([])

        self.assertIs(world.entities, before)
        self.assertEqual(world.getNumEntities(), 10)

    def test_none_is_treated_like_an_empty_batch(self):
        world = World()

        world.removeEntities(None)

        self.assertEqual(world.getNumEntities(), 10)

    def test_a_non_empty_batch_rebinds_the_entity_list(self):
        """The filtered list replaces the old one, so a reference taken via
        getEntities() before the call is left stale."""
        world = World()
        before = world.getEntities()

        world.removeEntities([world.Alison])

        self.assertIsNot(world.entities, before)
        self.assertIn(world.Alison, before)
        self.assertNotIn(world.Alison, world.getEntities())

    def test_matches_by_identity_not_by_name(self):
        world = World()

        world.removeEntities([LivingEntity("Alison")])

        self.assertEqual(world.getNumEntities(), 10)
        self.assertIn(world.Alison, world.getEntities())


class TestGetRandomEntity(unittest.TestCase):
    """getRandomEntity picks a uniformly random index, or None when empty."""

    def test_returns_none_when_the_world_is_empty(self):
        world = emptyWorld()

        self.assertIsNone(world.getRandomEntity())

    def test_rolls_over_the_full_index_range(self):
        world = World()

        with patch("world.world.random.randint", return_value=0) as randint:
            world.getRandomEntity()

        randint.assert_called_once_with(0, 9)

    def test_returns_the_entity_at_the_rolled_index(self):
        world = World()

        with patch("world.world.random.randint", return_value=3):
            self.assertIs(world.getRandomEntity(), world.Derrick)

    def test_a_single_entity_is_always_chosen(self):
        world = emptyWorld()
        only = LivingEntity("Only")
        world.addEntity(only)

        for i in range(20):
            self.assertIs(world.getRandomEntity(), only)

    def test_result_is_always_a_member_of_the_world(self):
        world = World()

        for i in range(50):
            self.assertIn(world.getRandomEntity(), world.getEntities())


class TestCullWeakestEntities(unittest.TestCase):
    """cullWeakestEntities trims the population down to a target, weakest
    first, never touching the protected entity."""

    def test_does_nothing_when_the_population_is_at_the_target(self):
        world = World()
        before = list(world.getEntities())

        removed = world.cullWeakestEntities(10)

        self.assertEqual(removed, [])
        self.assertEqual(world.getEntities(), before)

    def test_does_nothing_when_the_population_is_below_the_target(self):
        world = World()
        before = list(world.getEntities())

        removed = world.cullWeakestEntities(50)

        self.assertEqual(removed, [])
        self.assertEqual(world.getEntities(), before)

    def test_removes_exactly_enough_to_reach_the_target(self):
        world = World()

        removed = world.cullWeakestEntities(4)

        self.assertEqual(len(removed), 6)
        self.assertEqual(world.getNumEntities(), 4)

    def test_removes_the_lowest_health_entities_first(self):
        world = emptyWorld()
        strong = entityWithHealth("Strong", 100)
        middling = entityWithHealth("Middling", 60)
        weak = entityWithHealth("Weak", 20)
        for entity in (strong, weak, middling):
            world.addEntity(entity)

        removed = world.cullWeakestEntities(1)

        self.assertEqual(removed, [weak, middling])
        self.assertEqual(world.getEntities(), [strong])

    def test_returns_removed_entities_weakest_first(self):
        world = emptyWorld()
        entities = [entityWithHealth("E%d" % h, h) for h in (90, 30, 70, 10, 50)]
        for entity in entities:
            world.addEntity(entity)

        removed = world.cullWeakestEntities(2)

        self.assertEqual([e.health for e in removed], [10, 30, 50])

    def test_fewer_children_breaks_a_health_tie(self):
        world = emptyWorld()
        parent = entityWithHealth("Parent", 50, numChildren=2)
        childless = entityWithHealth("Childless", 50, numChildren=0)
        world.addEntity(parent)
        world.addEntity(childless)

        removed = world.cullWeakestEntities(1)

        self.assertEqual(removed, [childless])
        self.assertEqual(world.getEntities(), [parent])

    def test_health_outranks_children_in_the_sort(self):
        """A weak entity with many children is culled before a healthier
        one with none."""
        world = emptyWorld()
        weakParent = entityWithHealth("WeakParent", 10, numChildren=5)
        healthyLoner = entityWithHealth("HealthyLoner", 90, numChildren=0)
        world.addEntity(weakParent)
        world.addEntity(healthyLoner)

        removed = world.cullWeakestEntities(1)

        self.assertEqual(removed, [weakParent])

    def test_survivors_keep_their_original_order(self):
        world = emptyWorld()
        entities = [entityWithHealth("E%d" % h, h) for h in (90, 10, 70, 20, 50)]
        for entity in entities:
            world.addEntity(entity)

        world.cullWeakestEntities(3)

        self.assertEqual([e.health for e in world.getEntities()], [90, 70, 50])

    def test_protected_entity_survives_even_when_it_is_the_weakest(self):
        world = emptyWorld()
        player = entityWithHealth("Player", 1)
        others = [entityWithHealth("Other%d" % h, h) for h in (40, 60, 80)]
        world.addEntity(player)
        for other in others:
            world.addEntity(other)

        removed = world.cullWeakestEntities(2, protectedEntity=player)

        self.assertNotIn(player, removed)
        self.assertIn(player, world.getEntities())
        self.assertEqual([e.health for e in removed], [40, 60])
        self.assertEqual(world.getNumEntities(), 2)

    def test_protection_can_leave_the_population_above_the_target(self):
        """Only cullable entities are removed, so when the protected entity
        is the only one left the count stays above targetCount."""
        world = emptyWorld()
        player = entityWithHealth("Player", 100)
        other = entityWithHealth("Other", 50)
        world.addEntity(player)
        world.addEntity(other)

        removed = world.cullWeakestEntities(0, protectedEntity=player)

        self.assertEqual(removed, [other])
        self.assertEqual(world.getEntities(), [player])

    def test_returns_empty_when_only_the_protected_entity_remains(self):
        world = emptyWorld()
        player = entityWithHealth("Player", 100)
        world.addEntity(player)

        removed = world.cullWeakestEntities(0, protectedEntity=player)

        self.assertEqual(removed, [])
        self.assertEqual(world.getEntities(), [player])

    def test_protected_entity_outside_the_world_has_no_effect(self):
        world = emptyWorld()
        outsider = entityWithHealth("Outsider", 1)
        entities = [entityWithHealth("E%d" % h, h) for h in (30, 60)]
        for entity in entities:
            world.addEntity(entity)

        removed = world.cullWeakestEntities(1, protectedEntity=outsider)

        self.assertEqual([e.health for e in removed], [30])
        self.assertEqual([e.health for e in world.getEntities()], [60])

    def test_culling_does_not_alter_any_entity(self):
        world = emptyWorld()
        survivor = entityWithHealth("Survivor", 80, numChildren=1)
        victim = entityWithHealth("Victim", 20)
        world.addEntity(survivor)
        world.addEntity(victim)

        world.cullWeakestEntities(1)

        self.assertEqual(survivor.health, 80)
        self.assertEqual(len(survivor.children), 1)
        self.assertEqual(victim.health, 20)
        self.assertTrue(victim.isAlive())


if __name__ == "__main__":
    unittest.main()
