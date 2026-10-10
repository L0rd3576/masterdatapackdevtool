#!/usr/bin/env python3
"""Whole function-library suite in one command: header/index check, lint, server tests.

Usage: python tools/test_library.py [--only NAME] [--keep]
Exit 1 if INDEX.md is stale or any header is missing, if lint fails, or if any library test fails.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    tools = os.path.join(ROOT, "tools")
    r = subprocess.run([sys.executable, os.path.join(tools, "gen_library_index.py"), "--check"])
    if r.returncode:
        return 1
    r = subprocess.run([sys.executable, os.path.join(tools, "run_tests.py"), os.path.join(ROOT, "library", "mcdp_lib")]
                       + argv)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
