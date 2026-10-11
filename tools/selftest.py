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
    os.path.join(PACKS, "macro_facts"): (True, True, "macro substitution/call/return/context evidence"),
    os.path.join(PACKS, "bad_macro_call"): (False, False, "macro function called without a required key"),
    os.path.join(ROOT, "library", "mcdp_lib"): (True, True, "function library suite (library/INDEX.md)"),
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


def build_checks():
    """build_pack merge mode (E1) and pack_src overlay (E2) on a temp copy of examples/slice. Returns failures."""
    import contextlib
    import io
    import json
    import shutil
    import tempfile
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import build_pack
    from core import MapgenError
    tmp = tempfile.mkdtemp(prefix="bp_selftest_")
    out = os.path.join(tmp, "pack")
    src = os.path.join(out, "src")
    shutil.copytree(os.path.join(ROOT, "examples", "slice"), src, ignore=shutil.ignore_patterns("build"))
    pj = os.path.join(src, "project.json")
    proj = json.load(open(pj, encoding="utf-8"))
    proj.update(output="..", output_mode="merge")
    json.dump(proj, open(pj, "w", encoding="utf-8"), indent=2)
    os.makedirs(os.path.join(out, "data", "old", "function"))
    open(os.path.join(out, "data", "old", "function", "x.mcfunction"), "w").write("say old\n")
    open(os.path.join(out, "notes.md"), "w").write("foreign file\n")

    def attempt(**kw):
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                build_pack.build(src, validate=False, **kw)
                return None
            except MapgenError as e:
                return str(e)

    has = lambda *p: os.path.exists(os.path.join(out, *p))  # noqa: E731
    checks = []
    err = attempt()
    checks.append(("merge refuses data/ without .build_pack_owned", err is not None and "--adopt" in err
                   and has("data", "old")))
    err = attempt(adopt=True)
    checks.append(("--adopt takes over (old data/ gone, notes.md kept)", err is None and not has("data", "old")
                   and has("notes.md") and has(".build_pack_owned") and not has(".built_by_build_pack")
                   and has("data", "slice", "function", "extra", "tick.mcfunction") and has("src", "project.json")))
    open(os.path.join(out, "notes.md"), "a").write("edited\n")
    err = attempt()
    checks.append(("merge rebuild keeps a foreign file", err is None and has("notes.md") and
                   "edited" in open(os.path.join(out, "notes.md")).read() and has("tests", "j_extra_tick.test.json")))
    clash = os.path.join(src, "pack", "data", "__ns__", "function", "load.mcfunction")
    open(clash, "w").write("say clash\n")
    err = attempt()
    checks.append(("pack_src overlay collision is an ERROR naming both paths", err is not None and
                   "would override" in err and clash in err and os.path.join(out, "data", "slice", "function",
                                                                             "load.mcfunction") in err))
    os.remove(clash)
    proj.update(output="../..")
    inner = os.path.join(out, "data", "proj")
    shutil.copytree(src, inner)
    json.dump(proj, open(os.path.join(inner, "project.json"), "w", encoding="utf-8"), indent=2)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            build_pack.build(inner, validate=False)
            err = None
        except MapgenError as e:
            err = str(e)
    checks.append(("merge refuses a project inside out/data", err is not None and "lies inside" in err))
    shutil.rmtree(tmp, ignore_errors=True)
    bad = 0
    for name, ok in checks:
        bad += not ok
        print(f"[{'ok ' if ok else 'BAD'}] build     {name}")
    return bad


def main(argv):
    fast = "--fast" in argv
    bad = build_checks()
    code, out = run([os.path.join(ROOT, "tools", "lint_datapack.py"), vanilla_pack(), "--quiet"])
    bad += code != 0
    print(f"[{'ok ' if code == 0 else 'BAD'}] lint      vanilla data (all files) expected PASS  | {out.strip().splitlines()[-1]}")
    code, out = run([os.path.join(ROOT, "tools", "gen_library_index.py"), "--check"])
    bad += code != 0
    print(f"[{'ok ' if code == 0 else 'BAD'}] index     library headers + INDEX.md up to date | {out.strip().splitlines()[-1]}")
    code, out = run([os.path.join(ROOT, "tools", "mapgen", "selftest_failures.py")])
    bad += code != 0
    print(f"[{'ok ' if code == 0 else 'BAD'}] mapgen    3 broken fixtures rejected by their check | {out.strip().splitlines()[-1]}")
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
