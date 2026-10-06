# Kreatures

[![Play in your browser](https://img.shields.io/badge/Play-in%20your%20browser-2ea44f)](https://danielstephenson.dev/play/kreatures)

This game allows you to place a creature into a virtual environment with other creatures and observe its activity.

## Background
I created this application in 2017 as I was getting into python for the first time. It was one of the first programs that I was proud of.

## Main Idea
You're able to create a creature and release it into an environment where it can interact with other creatures.

## Ideas
- World already has creatures
- Every time creature comes into contact with another it has a chance to eat, become friends or have a baby
- The more you do one thing the less you do the others
- It has 4 different areas so that they're not all interacting with the same things
- Every day there's a chance they'll move areas

## Goals
- Show creatures alive at all times
- Make inputted names possible baby names using a txt file

## Usage reporting
Usage reporting is on by default: Kreatures sends one `startup` event per launch to [trace](https://danielstephenson.dev/usage-reporting) at `https://trace.danielstephenson.dev`, carrying only the program name, the version from `version.txt` and a random installation ID (the tag `install`, so installations can be counted rather than launches). Nothing about you or your machine is sent — no username, hostname, IP address, creature name or anything typed into the game. The report is made off the main thread and can never stop or slow the game.

The first launch prints a one-line notice and writes `src/config/settings.json` (git-ignored).

The installation ID is a random UUID kept in a file named `trace-install-id` in the user data directory: `~/.local/share/kreatures/` on Linux (or `$XDG_DATA_HOME/kreatures/`), `~/Library/Application Support/kreatures/` on macOS and `%APPDATA%\kreatures\` on Windows. It identifies no person, account or address; delete the file to get a new one. Setting the environment variable `TRACE_INSTALL_ID` sends that value instead and leaves the file alone. The file is only created while reporting is on, so every opt-out below also stops it. The browser version makes no ID file.

To turn reporting off, any one of these will do:

- `src/config/settings.json` → `"usage_reporting": {"enabled": false}` — Kreatures' own switch
- `TRACE_USAGE_REPORTING=off` (also `false`, `0`, `no`) in the environment — turns off every program that reports to trace
- `DO_NOT_TRACK=1` (also `true`, `yes`) in the environment — the [console DNT convention](https://consoledonottrack.com), honoured the same way

```json
{
  "usage_reporting": {
    "enabled": false
  }
}
```

The same block also holds `endpoint` and `key`, which are only there to be pointed at another trace server. The reporting client is `src/trace_client.py`, vendored unmodified from [trace-client-python](https://github.com/Stephenson-Software/trace-client-python) (0.4.0).

Details: https://danielstephenson.dev/usage-reporting

## Interakt & Apex
The ideas in this project are generalized and expanded upon in the [Interakt](https://github.com/Stephenson-Software/Interakt) and [Apex](https://github.com/Stephenson-Software/Apex) projects.

## Play in your browser
The same game, unmodified, runs in a browser tab under [tak](https://github.com/Stephenson-Software/tak)'s console runtime (Python via Pyodide): https://kreatures.play.danielstephenson.dev, listed with the rest at [danielstephenson.dev/play](https://danielstephenson.dev/play). To build and serve it locally (needs `tak` installed):
```
python3 web/build_zip.py
python3 -c "from tak.web.serve import main; main(root='.', title='Kreatures')"
```
Pushes to `master` deploy it to [arcade](https://github.com/Stephenson-Software/arcade) (`.github/workflows/browser.yml`).

