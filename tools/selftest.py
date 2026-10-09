#!/usr/bin/env python3
"""Prove the linter and test runner work: known-good packs must PASS, broken packs must FAIL.

Usage: python tools/selftest.py [--fast]     (--fast = linter only, no server)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "tools", "selftest")

# pack -> (lint should pass, run_tests should pass, why)
CASES = {
    os.path.join(ROOT, "template-datapack"): (True, True, "template is valid"),
    os.path.join(PACKS, "good"): (True, True, "ticks + entity movement + flat world layout"),
    os.path.join(PACKS, "runtime_facts"): (True, True, "26.3 NBT shapes, macros, return, schedule timing"),
    os.path.join(PACKS, "bad_command"):(False, False, "execute without run -> server 'Failed to load function'"),
    os.path.join(PACKS, "bad_json"): (False, False, "trailing comma in advancement -> server refuses to load"),
    os.path.join(PACKS, "missing_function"): (False, False, "function tag/ call to missing function"),
    os.path.join(PACKS, "failing_assert"): (True, False, "valid pack, wrong expectation -> expected/actual shown"),
    os.path.join(PACKS, "old_layout"): (False, False, "functions/ + tags/functions/ + pack_format only"),
}


def run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def vanilla_pack():
    """All vanilla data as one pack: the linter must report zero errors on it (false-positive check)."""
    import shutil
    dst = os.path.join(ROOT, "test-server", "vanilla-pack")
    if not os.path.isdir(dst):
        shutil.copytree(os.path.join(ROOT, "reference", "vanilla-data", "minecraft"),
                        os.path.join(dst, "data", "minecraft"), ignore=shutil.ignore_patterns("datapacks"))
        with open(os.path.join(dst, "pack.mcmeta"), "w") as f:
            f.write('{"pack":{"description":"vanilla","min_format":121,"max_format":121}}')
    return dst


def main(argv):
    fast = "--fast" in argv
    bad = 0
    code, out = run([os.path.join(ROOT, "tools", "lint_datapack.py"), vanilla_pack(), "--quiet"])
    bad += code != 0
    print(f"[{'ok ' if code == 0 else 'BAD'}] lint      vanilla data (all files) expected PASS  | {out.strip().splitlines()[-1]}")
    for pack, (lint_ok, tests_ok, why) in CASES.items():
        name = os.path.basename(pack)
        code, out = run([os.path.join(ROOT, "tools", "lint_datapack.py"), pack])
        got = code == 0
        status = "ok " if got == lint_ok else "BAD"
        bad += got != lint_ok
        print(f"[{status}] lint      {name:18} expected {'PASS' if lint_ok else 'FAIL'}, got {'PASS' if got else 'FAIL'}  ({why})")
        for line in out.strip().splitlines()[-3:]:
            print("          | " + line[:200])
        if fast:
            continue
        code, out = run([os.path.join(ROOT, "tools", "run_tests.py"), pack, "--skip-lint"])
        got = code == 0
        status = "ok " if got == tests_ok else "BAD"
        bad += got != tests_ok
        print(f"[{status}] run_tests {name:18} expected {'PASS' if tests_ok else 'FAIL'}, got {'PASS' if got else 'FAIL'}")
        for line in out.strip().splitlines():
            if "server log:" not in line:
                print("          | " + line[:200])
    print(f"selftest: {'PASS' if not bad else f'FAIL ({bad} unexpected result(s))'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
