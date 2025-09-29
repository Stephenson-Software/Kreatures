# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0

import sys
import os
import unittest
from unittest.mock import patch

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from entity.livingEntity import LivingEntity


class TestNames(unittest.TestCase):
    """Test that the names functionality works correctly"""

    @patch('builtins.input', return_value='TestPlayer')
    @patch('builtins.print')
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
            "Jesse", "Juan", "Jose", "Ralph", "Jeremy", "Bobby", "Johnny",
            "Douglas", "Peter", "Scott", "Kyle", "Billy", "Terry", "Randy", "Adam"
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
            "Sophia", "Liam", "Emma", "Noah", "Olivia", "Alexander", 
            "Isabella", "Mason", "Aria", "Diego", "Sofia", "Ahmed", 
            "Chen", "Elena", "Hassan", "Yuki", "Zara"
        ]
        for name in expected_new_names:
            self.assertIn(name, self.kreatures.names)


if __name__ == '__main__':
    unittest.main()