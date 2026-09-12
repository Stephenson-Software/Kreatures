# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
"""Tests for the usage-reporting wiring: the settings block in
src/config/settings.json, the one-time notice, the opt-out, and the startup
event arriving at a loopback stub. Nothing here contacts the real service."""
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import usage_reporting  # noqa: E402
from usage_reporting import (  # noqa: E402
    APPLICATION,
    DEFAULT_ENDPOINT,
    DEFAULT_KEY,
    FIRST_RUN_NOTICE,
    SETTINGS_FILE,
    buildClient,
    loadSettings,
    readVersion,
    startUsageReporting,
)


def stubServer(requests, arrived):
    """A loopback trace stand-in that records every POST and answers 201."""

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            requests.append(
                {
                    "path": self.path,
                    "authorization": self.headers.get("Authorization"),
                    "body": json.loads(self.rfile.read(length).decode("utf-8")),
                }
            )
            self.send_response(201)
            self.send_header("Content-Length", "0")
            self.end_headers()
            arrived.set()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class UsageReportingTestCase(unittest.TestCase):
    def setUp(self):
        self.tempDir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempDir.cleanup)
        self.settingsFile = os.path.join(self.tempDir.name, "settings.json")
        self.logged = []

    def log(self, message):
        self.logged.append(message)

    def readSettingsFile(self):
        with open(self.settingsFile, "r") as f:
            return json.load(f)

    def writeSettingsFile(self, settings):
        with open(self.settingsFile, "w") as f:
            json.dump(settings, f)


class TestSettings(UsageReportingTestCase):
    def test_first_run_writes_defaults_and_shows_the_notice_once(self):
        section = loadSettings(self.settingsFile, self.log)

        self.assertEqual(
            {"enabled": True, "endpoint": DEFAULT_ENDPOINT, "key": DEFAULT_KEY},
            section,
        )
        self.assertEqual([FIRST_RUN_NOTICE], self.logged)
        self.assertEqual({"usage_reporting": section}, self.readSettingsFile())

        self.logged.clear()
        secondRun = loadSettings(self.settingsFile, self.log)

        self.assertEqual(section, secondRun)
        self.assertEqual([], self.logged, "the notice must not be shown twice")

    def test_notice_names_the_program_the_service_and_the_opt_out(self):
        self.assertIn("Kreatures sends a startup event", FIRST_RUN_NOTICE)
        self.assertIn("program name and version only", FIRST_RUN_NOTICE)
        self.assertIn("trace.danielstephenson.dev", FIRST_RUN_NOTICE)
        self.assertIn('"usage_reporting": {"enabled": false}', FIRST_RUN_NOTICE)
        self.assertIn("src/config/settings.json", FIRST_RUN_NOTICE)

    def test_settings_file_lives_in_the_config_directory(self):
        self.assertEqual("settings.json", os.path.basename(SETTINGS_FILE))
        self.assertEqual("config", os.path.basename(os.path.dirname(SETTINGS_FILE)))

    def test_other_settings_in_an_existing_file_are_preserved(self):
        self.writeSettingsFile({"other": {"kept": 1}})

        loadSettings(self.settingsFile, self.log)

        self.assertEqual(
            {
                "other": {"kept": 1},
                "usage_reporting": usage_reporting.defaultSettings(),
            },
            self.readSettingsFile(),
        )
        self.assertEqual([FIRST_RUN_NOTICE], self.logged)

    def test_an_existing_block_is_returned_as_is_without_a_notice(self):
        self.writeSettingsFile({"usage_reporting": {"enabled": False}})

        section = loadSettings(self.settingsFile, self.log)

        self.assertEqual({"enabled": False}, section)
        self.assertEqual([], self.logged)
        self.assertEqual(
            {"usage_reporting": {"enabled": False}}, self.readSettingsFile()
        )

    def test_a_corrupt_file_disables_reporting_and_is_not_overwritten(self):
        with open(self.settingsFile, "w") as f:
            f.write("{not json")

        section = loadSettings(self.settingsFile, self.log)

        self.assertIsNone(section)
        self.assertEqual(1, len(self.logged))
        self.assertIn("usage reporting is off", self.logged[0])
        with open(self.settingsFile, "r") as f:
            self.assertEqual("{not json", f.read())

    def test_a_non_object_file_disables_reporting(self):
        self.writeSettingsFile([1, 2, 3])

        self.assertIsNone(loadSettings(self.settingsFile, self.log))

    def test_an_unwritable_file_still_returns_defaults_and_says_so(self):
        unwritable = os.path.join(self.tempDir.name, "missing", "settings.json")

        section = loadSettings(unwritable, self.log)

        self.assertEqual(usage_reporting.defaultSettings(), section)
        self.assertEqual(2, len(self.logged))
        self.assertEqual(FIRST_RUN_NOTICE, self.logged[0])
        self.assertIn("shown again next time", self.logged[1])


class TestBuildClient(unittest.TestCase):
    def test_none_settings_give_a_disabled_client(self):
        self.assertFalse(buildClient(None).enabled)

    def test_opt_out_gives_a_disabled_client(self):
        self.assertFalse(buildClient({"enabled": False}).enabled)

    def test_defaults_give_an_enabled_client(self):
        client = buildClient({"enabled": True})
        self.addCleanup(client.close)

        self.assertTrue(client.enabled)

    def test_missing_endpoint_and_key_fall_back_to_the_defaults(self):
        client = buildClient({"enabled": True, "endpoint": "", "key": None})
        self.addCleanup(client.close)

        self.assertTrue(client.enabled)
        self.assertEqual(DEFAULT_ENDPOINT + "/api/metrics", client._endpoint)
        self.assertEqual(DEFAULT_KEY, client._key)

    def test_an_empty_key_with_no_default_would_disable_but_the_default_is_set(self):
        self.assertTrue(DEFAULT_KEY)
        self.assertEqual("Kreatures", APPLICATION)


class TestVersion(unittest.TestCase):
    def test_version_comes_from_version_txt_at_the_repository_root(self):
        expected = os.path.join(os.path.dirname(__file__), "..", "version.txt")
        with open(expected, "r") as f:
            self.assertEqual(f.read().strip(), readVersion())

    def test_a_missing_version_file_gives_none(self):
        self.assertIsNone(readVersion("/nonexistent/version.txt"))


class TestStartup(UsageReportingTestCase):
    def setUp(self):
        super().setUp()
        self.requests = []
        self.arrived = threading.Event()
        self.server = stubServer(self.requests, self.arrived)
        self.addCleanup(self.server.shutdown)
        self.endpoint = "http://127.0.0.1:%d" % self.server.server_address[1]

    def test_startup_event_reaches_the_configured_endpoint(self):
        self.writeSettingsFile(
            {
                "usage_reporting": {
                    "enabled": True,
                    "endpoint": self.endpoint,
                    "key": "test-key",
                }
            }
        )

        client = startUsageReporting(self.settingsFile, self.log)
        self.addCleanup(client.close)

        self.assertTrue(self.arrived.wait(5), "the startup event never arrived")
        self.assertEqual(1, len(self.requests))
        request = self.requests[0]
        self.assertEqual("/api/metrics", request["path"])
        self.assertEqual("Bearer test-key", request["authorization"])
        self.assertEqual(
            {
                "application": "Kreatures",
                "name": "startup",
                "tags": {"version": readVersion()},
            },
            request["body"],
        )
        self.assertEqual([], self.logged)

    def test_opted_out_sends_nothing(self):
        self.writeSettingsFile(
            {
                "usage_reporting": {
                    "enabled": False,
                    "endpoint": self.endpoint,
                    "key": "test-key",
                }
            }
        )

        client = startUsageReporting(self.settingsFile, self.log)

        self.assertFalse(client.enabled)
        self.assertFalse(self.arrived.wait(0.5))
        self.assertEqual([], self.requests)

    def test_first_run_prints_the_notice_and_reports_to_the_default_endpoint(self):
        # The real default endpoint is production, so it is pointed at the
        # loopback stub for the duration of this test: nothing here may ever
        # reach trace.danielstephenson.dev.
        original = usage_reporting.DEFAULT_ENDPOINT
        usage_reporting.DEFAULT_ENDPOINT = self.endpoint
        self.addCleanup(setattr, usage_reporting, "DEFAULT_ENDPOINT", original)

        client = startUsageReporting(self.settingsFile, self.log)
        self.addCleanup(client.close)

        self.assertEqual([FIRST_RUN_NOTICE], self.logged)
        self.assertEqual(
            {"enabled": True, "endpoint": self.endpoint, "key": DEFAULT_KEY},
            self.readSettingsFile()["usage_reporting"],
        )
        self.assertTrue(self.arrived.wait(5), "the startup event never arrived")
        self.assertEqual("Bearer " + DEFAULT_KEY, self.requests[0]["authorization"])
        self.assertEqual("startup", self.requests[0]["body"]["name"])

        self.logged.clear()
        second = startUsageReporting(self.settingsFile, self.log)
        self.addCleanup(second.close)

        self.assertEqual(
            [], self.logged, "the notice must not be shown on the second run"
        )

    def test_never_raises_when_settings_loading_fails(self):
        def explode(*args, **kwargs):
            raise RuntimeError("boom")

        original = usage_reporting.loadSettings
        usage_reporting.loadSettings = explode
        self.addCleanup(setattr, usage_reporting, "loadSettings", original)

        client = startUsageReporting(self.settingsFile, self.log)

        self.assertFalse(client.enabled)


if __name__ == "__main__":
    unittest.main()
