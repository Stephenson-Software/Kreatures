# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
"""Characterization tests for the ``if __name__ == "__main__"`` block of
src/kreatures.py: what launching the game does, in what order.

The script is executed with runpy, the way ``python3 src/kreatures.py`` runs
it. usage_reporting.startUsageReporting is patched before the script imports
it, so nothing is sent and no settings file is written.
"""
import os
import runpy
import sys
import unittest
from unittest.mock import patch

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import usage_reporting  # noqa: E402 - must be importable before it is patched

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "src", "kreatures.py")


class StopLaunch(Exception):
    """Raised from a patched collaborator to end the launch at a known point."""


class TestEntryPoint(unittest.TestCase):
    def setUp(self):
        self.events = []

    def launch(self, runName="__main__", inputEffect=None, sleepEffect=None):
        """Run the script with reporting, input, print and sleep stubbed out,
        recording the order reporting and the name prompt happen in."""

        def report(*args, **kwargs):
            self.events.append("report")

        def prompt(*args, **kwargs):
            self.events.append("prompt")
            if inputEffect is not None:
                raise inputEffect
            return "TestPlayer"

        with patch.object(
            usage_reporting, "startUsageReporting", side_effect=report
        ), patch("builtins.input", side_effect=prompt), patch("builtins.print"), patch(
            "time.sleep", side_effect=sleepEffect
        ):
            runpy.run_path(SCRIPT, run_name=runName)

    def test_usage_is_reported_before_the_name_prompt(self):
        with self.assertRaises(StopLaunch):
            self.launch(inputEffect=StopLaunch())

        self.assertEqual(self.events, ["report", "prompt"])

    def test_a_player_who_quits_at_the_name_prompt_is_still_reported(self):
        with self.assertRaises(KeyboardInterrupt):
            self.launch(inputEffect=KeyboardInterrupt())

        self.assertIn("report", self.events)

    def test_usage_is_reported_once_per_launch(self):
        with self.assertRaises(StopLaunch):
            self.launch(sleepEffect=StopLaunch())

        self.assertEqual(self.events.count("report"), 1)

    def test_the_game_loop_starts_after_the_name_is_entered(self):
        """The first tick ends in time.sleep, so reaching it means run() was
        called on the game the name prompt built."""
        with self.assertRaises(StopLaunch):
            self.launch(sleepEffect=StopLaunch())

        self.assertEqual(self.events, ["report", "prompt"])

    def test_importing_the_module_neither_reports_nor_prompts(self):
        self.launch(runName="kreatures")

        self.assertEqual(self.events, [])


if __name__ == "__main__":
    unittest.main()
