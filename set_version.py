#!/usr/bin/env python3
"""
Configures the web application's version string.

For use when building a Docker image via a GitHub action.
"""

import os
import pathlib
import re

THIS_DIR = pathlib.Path(__file__).resolve().parent
INSTANCE_DIR = THIS_DIR / "instance"
VERSION_PY = INSTANCE_DIR / "version.py"


def main() -> None:
    version_string = "unknown"
    sha = None
    tag = None

    if ref := os.environ.get("GITHUB_REF"):
        if match := re.match(r"refs/tags/v(.+)", ref):
            tag = match.group(1)

    if sha := os.environ.get("GITHUB_SHA"):
        sha = sha[:8]

    if tag and sha:
        version_string = f"{tag}+{sha}"
    elif tag:
        version_string = tag
    elif sha:
        version_string = f"sha-{sha}"

    with open(VERSION_PY, mode="w", encoding="utf-8") as fp:
        print(f"SOTERIA_VERSION = {version_string!r}", file=fp)


if __name__ == "__main__":
    main()
