# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0

import sys
import os
import time
import unittest

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.livingEntity import LivingEntity
from world.world import World


class TestPerformance(unittest.TestCase):
	"""Performance tests to ensure simulation scales to tens of thousands of entities"""

	def test_large_entity_count_performance(self):
		"""Test that simulation handles 10,000 entities efficiently"""
		world = World()
		world.entities = []  # Clear starter entities

		# Create 10,000 entities
		num_entities = 10000
		for i in range(num_entities):
			entity = LivingEntity(f"Entity{i}")
			world.addEntity(entity)

		self.assertEqual(len(world.entities), num_entities)

		# Simulate 5 ticks and measure time
		num_ticks = 5
		start_time = time.time()

		for tick in range(num_ticks):
			entities_to_remove = set()  # Using set for O(1) lookup

			for entity in world.entities[:]:  # Create copy to avoid modification during iteration
				if len(world.entities) < 2:
					break

				target = world.getRandomEntity()
				if target == entity:
					continue

				# Simulate basic interaction
				decision = entity.getNextAction(target)
				if decision == "fight":
					entity.increaseChanceToFight()
				elif decision == "befriend":
					entity.befriend(target)
				elif decision == "love":
					entity.increaseChanceToBefriend()

			# Remove dead entities
			for entity in entities_to_remove:
				if entity in world.entities:
					world.removeEntity(entity)

		elapsed = time.time() - start_time
		avg_time_per_tick = elapsed / num_ticks

		# Should complete in reasonable time (less than 0.1s per tick for 10k entities)
		self.assertLess(
			avg_time_per_tick,
			0.1,
			f"Performance degraded: {avg_time_per_tick:.4f}s per tick for {num_entities} entities",
		)

		print(
			f"\nPerformance test passed: {avg_time_per_tick:.4f}s per tick for {num_entities} entities"
		)

	def test_friends_list_performance(self):
		"""Test that friend lookups are fast even with many friends"""
		entity1 = LivingEntity("Entity1")
		entity2 = LivingEntity("Entity2")

		# Add many friends
		num_friends = 1000
		friends = []
		for i in range(num_friends):
			friend = LivingEntity(f"Friend{i}")
			friends.append(friend)
			entity1.friends.add(friend)  # Should use set for O(1) lookup

		# Measure lookup time
		start_time = time.time()
		for _ in range(1000):
			# Check if entity2 is a friend (not in the list)
			is_friend = entity2 in entity1.friends

		elapsed = time.time() - start_time

		# Should be very fast with set-based lookup
		self.assertLess(
			elapsed, 0.01, f"Friend lookup too slow: {elapsed:.4f}s for 1000 checks"
		)

	def test_entity_removal_performance(self):
		"""Test that entity removal is efficient with large populations"""
		world = World()
		world.entities = []

		# Create 5000 entities
		num_entities = 5000
		for i in range(num_entities):
			entity = LivingEntity(f"Entity{i}")
			world.addEntity(entity)

		# Track entities to remove using set
		entities_to_remove = set()
		for i in range(0, num_entities, 2):  # Remove half
			entities_to_remove.add(world.entities[i])

		# Measure removal time
		start_time = time.time()
		for entity in entities_to_remove:
			world.removeEntity(entity)
		elapsed = time.time() - start_time

		# Should complete quickly
		self.assertLess(
			elapsed, 0.1, f"Entity removal too slow: {elapsed:.4f}s for 2500 removals"
		)
		self.assertEqual(len(world.entities), num_entities // 2)


if __name__ == "__main__":
	unittest.main()
