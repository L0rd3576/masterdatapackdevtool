"""Deliberate-failure self-tests for the map/framework tooling: each fixture in tools/mapgen/selftest/ is broken in
exactly one way and must be rejected by exactly the check that targets it.

  missing_key.json        validate.py        -> ERROR missing required key 'players'
  unreachable_spawn.json  report.py          -> ERROR spawn_reachability (only)
  nondeterministic.json   report.py          -> ERROR determinism (only)

Usage:
    python tools/mapgen/selftest_failures.py      exit 0 if every fixture fails as expected
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "selftest")
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "build", "selftest")

CASES = [
    ("missing required key", [os.path.join(HERE, "validate.py"), "--kind", "map",
                              os.path.join(FIX, "missing_key.json")],
     r"missing required key 'players'", None),
    ("unreachable spawn", [os.path.join(HERE, "report.py"), os.path.join(FIX, "unreachable_spawn.json"),
                           "--no-server", "--out", OUT, "--plugin-dir", os.path.join(FIX, "plugins")],
     r"ERROR spawn_reachability", "spawn_reachability"),
    ("non-deterministic generator", [os.path.join(HERE, "report.py"), os.path.join(FIX, "nondeterministic.json"),
                                     "--no-server", "--out", OUT, "--plugin-dir", os.path.join(FIX, "plugins")],
     r"ERROR determinism", "determinism"),
]


def main():
    bad = 0
    for name, args, expect, only in CASES:
        r = subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=ROOT)
        out = r.stdout + r.stderr
        errors = re.findall(r"ERROR (\w+):", out)
        ok = r.returncode == 1 and re.search(expect, out)
        if ok and only:
            ok = set(errors) == {only}
        print(f"{'PASS' if ok else 'FAIL'}  {name}: exit {r.returncode}, expected /{expect}/"
              + (f", errors from {sorted(set(errors))}" if only else ""))
        for line in out.splitlines():
            if "ERROR" in line:
                print("      " + line.strip())
        bad += not ok
    print(f"RESULT: {'PASS' if not bad else 'FAIL'} ({len(CASES) - bad}/{len(CASES)} fixtures rejected as expected)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
