# @author Daniel McCoy Stephenson
"""Build the browser version of Kreatures: web/index.html and web/game.zip.

The game runs unmodified in the browser under tak's console runtime
(https://github.com/Stephenson-Software/tak, tak.web.console): its prompts and
output go to a terminal on the page, and any file it writes is kept in the
browser. Needs tak installed (see .github/workflows/browser.yml). Serve the
result cross-origin isolated, e.g. with arcade or tak.web.serve:

    python3 web/build_zip.py
    python3 -c "from tak.web.serve import main; main(root='.', title='Kreatures')"
"""

import os

from tak.web.bundle import build
from tak.web.console import page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "web", "index.html"), "w", encoding="utf-8") as out:
    out.write(
        page(
            title='Kreatures',
            tagline='name a creature and watch its world',
            entry='src/kreatures.py',
            idbName='kreatures-files',
            footer='More by Daniel Stephenson &rarr; <a href="https://danielstephenson.dev/play">danielstephenson.dev/play</a>',
        )
    )

build(root=ROOT, sourceDirectories=('src',), extraFiles=('version.txt',))
