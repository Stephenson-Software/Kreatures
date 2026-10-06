# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
"""Reports one anonymous ``startup`` event per launch to the trace service.

Kreatures has no settings file of its own (``config/config.py`` is a class of
defaults), so the ``usage_reporting`` block lives in ``config/settings.json``
next to ``names.json``, the one configuration file the project already reads.
The file is created on the first launch after this was added, together with a
single printed notice saying that reporting is on and how to turn it off.

Every event also carries a random installation ID (the tag ``install``) so
installations can be counted rather than launches: ``TRACE_INSTALL_ID`` when
set, otherwise a UUID the client keeps in ``installIdFile()``. The browser
build gets no ID file (see ``installIdFile``).

Two environment variables every trace client honours also turn it off:
``TRACE_USAGE_REPORTING=off`` and ``DO_NOT_TRACK=1``. The client checks them
in its constructor, before the settings block, so they win even when the
block says on - and a first launch with either set writes nothing and says
nothing, so the notice is still waiting for the first launch that reports.
Details: https://danielstephenson.dev/usage-reporting
"""
import atexit
import json
import os
import sys

from trace_client import TraceClient, environment_opts_out

# @author Daniel McCoy Stephenson
# @since September 11th, 2026

APPLICATION = "Kreatures"
SETTINGS_SECTION = "usage_reporting"
DEFAULT_ENDPOINT = "https://trace.danielstephenson.dev"
DEFAULT_KEY = "oeuGjgm4fLkWt2WREm5L1-t_jOM7yvdjm8GVr8A8bYo"

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(_SRC_DIR, "config", "settings.json")
VERSION_FILE = os.path.join(_SRC_DIR, "..", "version.txt")

DETAILS_URL = "https://danielstephenson.dev/usage-reporting"

FIRST_RUN_NOTICE = (
    "Usage reporting is on: Kreatures sends a startup event (program name, "
    "version and a random installation ID only) to trace.danielstephenson.dev. "
    'Turn it off with "usage_reporting": {"enabled": false} in src/config/settings.json '
    "or TRACE_USAGE_REPORTING=off in the environment. Details: " + DETAILS_URL
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


def installIdFile():
    """Where this installation's random ID (the tag ``install``) is kept:
    ``<user data dir>/kreatures/trace-install-id``, the user data dir being
    %APPDATA% on Windows, ~/Library/Application Support on macOS and
    $XDG_DATA_HOME (or ~/.local/share) elsewhere. The client only reads or
    creates it when reporting is on; deleting it resets the ID.

    None in the browser build (tak's console runtime): the browser has no
    stable user data directory, and Kreatures keeps nothing in localStorage
    to hold an ID instead, so no ID is made there."""
    if sys.platform == "emscripten":
        return None
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", "").strip() or os.path.join(
            home, "AppData", "Roaming"
        )
    elif sys.platform == "darwin":
        base = os.path.join(home, "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME", "").strip() or os.path.join(
            home, ".local", "share"
        )
    return os.path.join(base, APPLICATION.lower(), "trace-install-id")


def programVersion():
    """The version every event is tagged with: version.txt's, or "unknown"
    when it cannot be read, so a missing file never stops startup."""
    return readVersion() or "unknown"


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

    if environment_opts_out():
        # Nothing will be sent this run, so saying "reporting is on" would be
        # wrong and writing the block would silence the notice for good. The
        # defaults are returned unwritten; the client sees the environment.
        return defaultSettings()

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
    """A TraceClient for the given usage_reporting settings; disabled when
    they are None or opted out. Always built through the client's constructor,
    which puts TRACE_USAGE_REPORTING / DO_NOT_TRACK ahead of the settings and
    records why it is off in ``disabled_reason``. The installation ID
    (TRACE_INSTALL_ID, else installIdFile()) is resolved by the client only
    after those checks, so a disabled client never creates the file."""
    if section is None:
        return TraceClient.disabled()
    enabled = section.get("enabled", True)
    endpoint = section.get("endpoint") or DEFAULT_ENDPOINT
    key = section.get("key") or DEFAULT_KEY
    try:
        return TraceClient(
            endpoint,
            APPLICATION,
            programVersion(),
            key=key,
            enabled=bool(enabled),
            install_id=os.environ.get("TRACE_INSTALL_ID"),
            install_id_file=installIdFile(),
        )
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
    client.report("startup")
    atexit.register(client.close)
    return client
