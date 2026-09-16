# Kreatures
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
Usage reporting is on by default: Kreatures sends one `startup` event per launch to [trace](https://github.com/Stephenson-Software/trace) at `https://trace.danielstephenson.dev`, carrying only the program name and the version from `version.txt`. Nothing about you or your machine is sent — no username, hostname, IP address, creature name or anything typed into the game. The report is made off the main thread and can never stop or slow the game.

The first launch prints a one-line notice and writes `src/config/settings.json` (git-ignored). To turn reporting off, any one of these will do:

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

The same block also holds `endpoint` and `key`, which are only there to be pointed at another trace server. The reporting client is `src/trace_client.py`, vendored unmodified from [trace-client-python](https://github.com/Stephenson-Software/trace-client-python) (0.2.0).

Details: https://github.com/Stephenson-Software/trace#usage-reporting

## Interakt & Apex
The ideas in this project are generalized and expanded upon in the [Interakt](https://github.com/Stephenson-Software/Interakt) and [Apex](https://github.com/Stephenson-Software/Apex) projects.
