# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
import os
import unittest

SRC = os.path.join(os.path.dirname(__file__), "..", "src")


class TestPackageStructure(unittest.TestCase):
    """`.github/copilot-instructions.md` requires an `__init__.py` per module.

    Without one a directory is still importable as an implicit namespace
    package, so nothing fails at run time and a missing file goes unnoticed —
    which is how `src/world` went without one. `find_packages()` skips such a
    directory by default, so the omission would only surface at packaging time.
    """

    def getPackageDirectories(self):
        return [
            entry
            for entry in sorted(os.listdir(SRC))
            if os.path.isdir(os.path.join(SRC, entry)) and entry != "__pycache__"
        ]

    def test_every_source_directory_is_a_regular_package(self):
        missing = [
            directory
            for directory in self.getPackageDirectories()
            if not os.path.isfile(os.path.join(SRC, directory, "__init__.py"))
        ]

        self.assertEqual(
            missing, [], "src/%s has no __init__.py" % ", src/".join(missing)
        )

    def test_src_itself_is_a_regular_package(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC, "__init__.py")))

    def test_the_expected_packages_are_all_present(self):
        self.assertEqual(
            self.getPackageDirectories(),
            ["config", "entity", "flags", "stats", "world"],
        )


if __name__ == "__main__":
    unittest.main()
