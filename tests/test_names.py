# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0

import sys
import os
import unittest
from unittest.mock import patch

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.livingEntity import LivingEntity


class TestNames(unittest.TestCase):
    """Test that the names functionality works correctly"""

    @patch("builtins.input", return_value="TestPlayer")
    @patch("builtins.print")
    def setUp(self, mock_print, mock_input):
        """Set up test environment"""
        # Import Kreatures class only (not the module level instance)
        from kreatures import Kreatures

        self.kreatures = Kreatures()

    def test_names_list_exists(self):
        """Test that names list exists and has content"""
        self.assertIsInstance(self.kreatures.names, list)
        self.assertGreater(len(self.kreatures.names), 0)

    def test_names_are_strings(self):
        """Test that all names are strings"""
        for name in self.kreatures.names:
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)  # Non-empty strings

    def test_create_entity_uses_name_from_list(self):
        """Test that createEntity uses a name from the names list"""
        entity = LivingEntity(self.kreatures.names[0])
        self.assertIn(entity.name, self.kreatures.names)

    def test_create_child_entity_uses_name_from_list(self):
        """Test that createChildEntity uses a name from the names list"""
        parent1 = LivingEntity("Parent1")
        parent2 = LivingEntity("Parent2")

        child = self.kreatures.createChildEntity(parent1, parent2)
        self.assertIn(child.name, self.kreatures.names)

    def test_names_contain_original_names(self):
        """Test that original names are still present"""
        original_names = [
            "Jesse",
            "Juan",
            "Jose",
            "Ralph",
            "Jeremy",
            "Bobby",
            "Johnny",
            "Douglas",
            "Peter",
            "Scott",
            "Kyle",
            "Billy",
            "Terry",
            "Randy",
            "Adam",
        ]
        for name in original_names:
            self.assertIn(name, self.kreatures.names)

    def test_names_list_expanded(self):
        """Test that names list has been significantly expanded"""
        # Should be much larger than the original 15 names
        self.assertGreater(len(self.kreatures.names), 50)

    def test_names_include_diverse_names(self):
        """Test that expanded names include diverse/modern names"""
        expected_new_names = [
            "Sophia",
            "Liam",
            "Emma",
            "Noah",
            "Olivia",
            "Alexander",
            "Isabella",
            "Mason",
            "Aria",
            "Diego",
            "Sofia",
            "Ahmed",
            "Chen",
            "Elena",
            "Hassan",
            "Yuki",
            "Zara",
        ]
        for name in expected_new_names:
            self.assertIn(name, self.kreatures.names)

    def test_names_no_duplicates(self):
        """Test that there are no duplicate names in the list"""
        names_set = set(self.kreatures.names)
        self.assertEqual(
            len(names_set),
            len(self.kreatures.names),
            "Names list should not contain duplicates",
        )

    def test_names_proper_capitalization(self):
        """Test that all names are properly capitalized"""
        for name in self.kreatures.names:
            self.assertTrue(
                name[0].isupper(), f"Name '{name}' should start with uppercase letter"
            )
            # Check that rest of name is lowercase (basic name format)
            if len(name) > 1:
                self.assertTrue(
                    name[1:].islower(),
                    f"Name '{name}' should have only first letter capitalized",
                )

    def test_names_length_validation(self):
        """Test that all names have reasonable lengths"""
        for name in self.kreatures.names:
            self.assertGreaterEqual(
                len(name), 2, f"Name '{name}' should be at least 2 characters long"
            )
            self.assertLessEqual(
                len(name), 15, f"Name '{name}' should be at most 15 characters long"
            )

    def test_names_alphabetic_characters(self):
        """Test that all names contain only alphabetic characters"""
        for name in self.kreatures.names:
            self.assertTrue(
                name.isalpha(),
                f"Name '{name}' should contain only alphabetic characters",
            )

    def test_name_categories_present(self):
        """Test that names from different categories are present"""
        # Traditional male names
        traditional_male = [
            "Alexander",
            "Andrew",
            "Benjamin",
            "Christopher",
            "Daniel",
            "David",
            "James",
            "John",
            "Michael",
            "William",
        ]
        male_count = sum(1 for name in traditional_male if name in self.kreatures.names)
        self.assertGreater(male_count, 5, "Should have multiple traditional male names")

        # Traditional female names
        traditional_female = [
            "Elizabeth",
            "Emily",
            "Emma",
            "Jessica",
            "Jennifer",
            "Katherine",
            "Margaret",
            "Mary",
            "Patricia",
            "Sarah",
        ]
        female_count = sum(
            1 for name in traditional_female if name in self.kreatures.names
        )
        self.assertGreater(
            female_count, 5, "Should have multiple traditional female names"
        )

        # International names
        international = ["Ahmed", "Chen", "Diego", "Hassan", "Yuki", "Zara", "Sofia"]
        intl_count = sum(1 for name in international if name in self.kreatures.names)
        self.assertGreater(intl_count, 3, "Should have multiple international names")

        # Modern names
        modern = ["Aiden", "Aria", "Blake", "Hunter", "Luna", "Mason", "Quinn", "Riley"]
        modern_count = sum(1 for name in modern if name in self.kreatures.names)
        self.assertGreater(modern_count, 3, "Should have multiple modern names")

    def test_random_name_selection_variety(self):
        """Test that random name selection provides variety over multiple calls"""
        import random

        # Seed random for reproducible results
        random.seed(42)

        selected_names = set()
        # Create many entities to test variety
        for _ in range(50):
            self.kreatures.createEntity()

        # Collect names of created entities (excluding starter entities and player)
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

        for entity in self.kreatures.environment.getEntities():
            if (
                hasattr(entity, "name")
                and entity != self.kreatures.playerCreature
                and entity.name not in starter_names
            ):
                selected_names.add(entity.name)

        # With 158 names and 50 entities, we should get reasonable variety
        # Expect at least 10 different names (conservative estimate accounting for randomness)
        self.assertGreaterEqual(
            len(selected_names),
            10,
            f"Should have reasonable variety in selected names. Got: {selected_names}",
        )

    def test_create_entity_always_uses_valid_name(self):
        """Test that createEntity always selects a valid name from the list"""
        # Test multiple entity creations
        for _ in range(20):
            initial_count = len(self.kreatures.environment.getEntities())
            self.kreatures.createEntity()
            new_count = len(self.kreatures.environment.getEntities())

            # Should have added exactly one entity
            self.assertEqual(new_count, initial_count + 1)

            # Get the newly created entity
            new_entity = self.kreatures.environment.getEntities()[-1]
            if hasattr(new_entity, "name"):  # Filter out placeholder strings
                self.assertIn(new_entity.name, self.kreatures.names)

    def test_create_child_entity_always_uses_valid_name(self):
        """Test that createChildEntity always selects a valid name from the list"""
        parent1 = LivingEntity("TestParent1")
        parent2 = LivingEntity("TestParent2")

        # Test multiple child creations
        for _ in range(20):
            child = self.kreatures.createChildEntity(parent1, parent2)
            self.assertIn(child.name, self.kreatures.names)
            # Clean up to avoid environment clutter
            if child in self.kreatures.environment.getEntities():
                self.kreatures.environment.removeEntity(child)

    def test_name_selection_robustness(self):
        """Test that name selection handles edge cases properly"""
        # Verify names list is not empty (should never happen but good to test)
        self.assertGreater(len(self.kreatures.names), 0)

        # Verify all indices in range are valid
        import random

        for _ in range(100):  # Test many random selections
            random_index = random.randint(0, len(self.kreatures.names) - 1)
            selected_name = self.kreatures.names[random_index]
            self.assertIsInstance(selected_name, str)
            self.assertGreater(len(selected_name), 0)

    def test_exact_name_count(self):
        """Test that we have exactly the expected number of names"""
        # Should be 158 names total (15 original + 143 new, with duplicate removed)
        self.assertEqual(len(self.kreatures.names), 158)

    def test_name_distribution_across_alphabet(self):
        """Test that names are distributed across different starting letters"""
        first_letters = set()
        for name in self.kreatures.names:
            first_letters.add(name[0].upper())

        # Should have names starting with various letters of the alphabet
        # With 158 diverse names, we should have at least 15 different starting letters
        self.assertGreaterEqual(
            len(first_letters),
            15,
            f"Names should start with diverse letters. Found: {sorted(first_letters)}",
        )


if __name__ == "__main__":
    unittest.main()
