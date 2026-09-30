# Copyright (c) 2022 Daniel McCoy Stephenson
# Apache License 2.0
import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
SCRIPTS = ["format.sh", "run.sh", "test.sh"]


class TestScripts(unittest.TestCase):
    """The helper scripts must run under bash and Python 3.

    The codebase is Python 3 only, but bare `python` is Python 2 on some
    machines and absent on others. CI never noticed because
    `actions/setup-python` points `python` at 3.x.
    """

    def readScript(self, name):
        with open(os.path.join(ROOT, name)) as file:
            return file.read()

    def test_every_script_starts_with_a_bash_shebang(self):
        for name in SCRIPTS:
            with self.subTest(script=name):
                firstLine = self.readScript(name).splitlines()[0]
                self.assertEqual(firstLine, "#!/bin/bash")

    def test_no_script_invokes_bare_python(self):
        for name in SCRIPTS:
            with self.subTest(script=name):
                for line in self.readScript(name).splitlines():
                    if line.lstrip().startswith("#"):
                        continue
                    self.assertIsNone(
                        re.search(r"\bpython\b", line),
                        "%s calls bare python: %s" % (name, line.strip()),
                    )


if __name__ == "__main__":
    unittest.main()
