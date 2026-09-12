# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
"""Reports one anonymous ``startup`` event per launch to the trace service.

Kreatures has no settings file of its own (``config/config.py`` is a class of
defaults), so the ``usage_reporting`` block lives in ``config/settings.json``
next to ``names.json``, the one configuration file the project already reads.
The file is created on the first launch after this was added, together with a
single printed notice saying that reporting is on and how to turn it off.
"""
import atexit
import json
import os

from trace_client import TraceClient

# @author Daniel McCoy Stephenson
# @since September 11th, 2026

APPLICATION = "Kreatures"
SETTINGS_SECTION = "usage_reporting"
DEFAULT_ENDPOINT = "https://trace.danielstephenson.dev"
DEFAULT_KEY = "oeuGjgm4fLkWt2WREm5L1-t_jOM7yvdjm8GVr8A8bYo"

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(_SRC_DIR, "config", "settings.json")
VERSION_FILE = os.path.join(_SRC_DIR, "..", "version.txt")

FIRST_RUN_NOTICE = (
    "Usage reporting is on: Kreatures sends a startup event (program name and "
    "version only) to trace.danielstephenson.dev. "
    'Turn it off with "usage_reporting": {"enabled": false} in src/config/settings.json.'
)


def defaultSettings():
    """The usage_reporting block written to settings.json on first run."""
    return {"enabled": True, "endpoint": DEFAULT_ENDPOINT, "key": DEFAULT_KEY}


def readVersion(versionFile=VERSION_FILE):
    """The program's own version as recorded in version.txt, or None if it cannot be read."""
    try:
        with open(versionFile, "r") as f:
            version = f.read().strip()
        return version or None
    except OSError:
        return None


def loadSettings(settingsFile=SETTINGS_FILE, log=print):
    """Read the usage_reporting block from the settings file, writing the
    default block (and printing the one-time notice) when the file does not
    have one yet.

    Returns the usage_reporting settings, or None if the settings file exists
    but cannot be read, in which case nothing is reported and the file is left
    alone.
    """
    settings = {}
    if os.path.exists(settingsFile):
        try:
            with open(settingsFile, "r") as f:
                settings = json.load(f)
            if not isinstance(settings, dict):
                raise ValueError("settings file is not a JSON object")
        except (OSError, ValueError) as e:
            log(
                "Could not read %s (%s); usage reporting is off until it is fixed."
                % (settingsFile, e)
            )
            return None

    section = settings.get(SETTINGS_SECTION)
    if isinstance(section, dict):
        return section

    settings[SETTINGS_SECTION] = defaultSettings()
    log(FIRST_RUN_NOTICE)
    try:
        with open(settingsFile, "w") as f:
            json.dump(settings, f, indent=2)
            f.write("\n")
    except OSError as e:
        log(
            "Could not write %s (%s); the notice above will be shown again next time."
            % (settingsFile, e)
        )
    return settings[SETTINGS_SECTION]


def buildClient(section):
    """A TraceClient for the given usage_reporting settings; disabled when they are None or opted out."""
    if section is None:
        return TraceClient.disabled()
    enabled = section.get("enabled", True)
    endpoint = section.get("endpoint") or DEFAULT_ENDPOINT
    key = section.get("key") or DEFAULT_KEY
    try:
        return TraceClient(endpoint, APPLICATION, key=key, enabled=bool(enabled))
    except Exception:
        return TraceClient.disabled()


def startUsageReporting(settingsFile=SETTINGS_FILE, log=print):
    """Read the settings, build the client and report the startup event.

    Never raises; the client is closed automatically when the interpreter
    exits. Returns the client so further events could be reported.
    """
    try:
        client = buildClient(loadSettings(settingsFile, log))
    except Exception:
        return TraceClient.disabled()
    version = readVersion()
    client.report("startup", tags={"version": version} if version else None)
    atexit.register(client.close)
    return client
