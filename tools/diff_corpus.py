#!/usr/bin/env python3
"""Differential test: linter vs. real 26.3 server on a corpus of single-line functions.

Usage:
    python tools/diff_corpus.py [tools/corpus/commands.txt] [--show-all]

Each corpus line becomes function c:lNNNN. The server's load log says which functions failed to parse;
the linter's verdict is compared. Exit 1 if the linter ACCEPTS a line the server REJECTS (a linter gap)
or REJECTS a line the server accepts that is not marked '## lint-only' (a false positive).
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_tests  # noqa: E402

ROOT = run_tests.ROOT
VANILLA = os.path.join(ROOT, "reference", "vanilla-data", "minecraft")
PACK = os.path.join(ROOT, "test-server", "corpus-pack")


def build(lines, with_json):
    shutil.rmtree(PACK, ignore_errors=True)
    fn = os.path.join(PACK, "data", "c", "function")
    os.makedirs(fn)
    with open(os.path.join(PACK, "pack.mcmeta"), "w") as f:
        json.dump({"pack": {"description": "corpus", "min_format": 121, "max_format": 121}}, f)
    support = {
        "function/helper.mcfunction": "say helper\n",
        "function/macro.mcfunction": "$say $(name)\n",
        "tags/function/mytag.json": json.dumps({"values": ["c:helper"]}),
        "item_modifier/my_modifier.json": json.dumps({"type": "minecraft:set_count", "count": 2}),
    }
    for rel, text in support.items():
        p = os.path.join(PACK, "data", "c", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)
    for src, dst in (("predicate/tool/can_shear.json", "predicate/is_sneaking.json"),
                     ("loot_table/chests/simple_dungeon.json", "loot_table/my_loot.json")):
        p = os.path.join(PACK, "data", "c", dst)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copy(os.path.join(VANILLA, src), p)
    jroot = os.path.join(ROOT, "tools", "corpus", "json")
    for dirpath, _, files in os.walk(jroot if with_json else os.devnull + "_none"):
        for jf in files:
            rel = os.path.relpath(os.path.join(dirpath, jf), jroot)
            dst = os.path.join(PACK, "data", "j", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.join(dirpath, jf), dst)
    for i, (_, cmd, _) in enumerate(lines):
        with open(os.path.join(fn, f"l{i:04d}.mcfunction"), "w", encoding="utf-8") as f:
            f.write(cmd + "\n")


def boot():
    server = run_tests.Server(PACK)
    server.prepare()
    try:
        started = server.start()
        return started, server.log_since(0)
    finally:
        server.stop()


def main(argv):
    corpus = next((a for a in argv if not a.startswith("--")), os.path.join(ROOT, "tools", "corpus", "commands.txt"))
    lines = []
    for n, raw in enumerate(open(corpus, encoding="utf-8"), 1):
        raw = raw.rstrip("\n")
        if not raw.strip() or raw.startswith("# "):
            continue
        flag = "lint" if raw.endswith("## lint-only") else "server" if raw.endswith("## server-only") else None
        lines.append((n, raw.replace("## lint-only", "").replace("## server-only", "").rstrip(), flag))
    build(lines, with_json=True)

    lint = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lint_datapack.py"), PACK],
                          capture_output=True, text=True)
    lint_err = {}
    for l in lint.stdout.splitlines():
        m = re.match(r"ERROR data/c/function/l(\d{4})\.mcfunction(?::\d+)?: (.*)", l)
        if m:
            lint_err.setdefault(int(m.group(1)), m.group(2))
    other = [l for l in lint.stdout.splitlines() if l.startswith("ERROR") and "/function/l" not in l
             and not l.startswith("ERROR data/j/")]
    jroot = os.path.join(ROOT, "tools", "corpus", "json")
    jcases = sorted(os.path.relpath(os.path.join(d, f), jroot).replace(os.sep, "/")
                    for d, _, fs in os.walk(jroot) for f in fs)
    jlint = {}
    for l in lint.stdout.splitlines():
        m = re.match(r"ERROR data/j/(\S+?): (.*)", l)
        if m:
            jlint.setdefault(m.group(1), m.group(2))

    # Run 1: JSON corpus only (registry errors abort the server before functions load).
    build([], with_json=True)
    _, log = boot()
    jsrv = {}
    text = "\n".join(log)
    for case in jcases:
        name = os.path.splitext(case.split("/")[-1])[0]
        m = re.search(r"(?:element|tag|references:)[^\n]*\bj:" + re.escape(name) + r"\b[^\n]*(?:\n(?!\[|>>).*){0,12}", text)
        if m:
            jsrv[case] = " | ".join(x.strip() for x in m.group(0).splitlines()
                                    if x.strip() and not x.strip().startswith("at ") and "Failed to parse" not in x)[:600]
    # Run 2: command corpus + support files.
    build(lines, with_json=False)
    started, log = boot()
    if not started:
        print("server did not start for the command corpus; see test-server/last-run.log")
        return 1
    srv_err = {}
    for i, l in enumerate(log):
        m = re.search(r"Failed to load function c:l(\d{4})", l)
        if m:
            detail = log[i + 1] if i + 1 < len(log) else ""
            srv_err[int(m.group(1))] = re.sub(r"^.*?IllegalArgumentException: ", "", detail)
    load_errs = [b for b in run_tests.datapack_errors(log) if not any("c:l" in x for x in b)]
    for b in load_errs:
        print("SUPPORT FILE ERROR: " + " | ".join(b))
    for l in other:
        print("LINT (support files): " + l)

    gaps, fps, agree = [], [], 0
    for i, (n, cmd, lint_only) in enumerate(lines):
        s_bad, l_bad = i in srv_err, i in lint_err
        if s_bad and not l_bad and lint_only == "server":
            agree += 1   # argument types the linter only checks shallowly (slot sources, number providers)
            if "--show-all" in argv:
                print(f"  REJECT line {n} (server-only): {cmd}\n     server: {srv_err[i]}")
        elif s_bad and not l_bad:
            gaps.append(f"  line {n}: {cmd}\n     server: {srv_err[i]}")
        elif l_bad and not s_bad and lint_only != "lint":
            fps.append(f"  line {n}: {cmd}\n     linter: {lint_err[i]}")
        elif lint_only == "lint" and not l_bad:
            gaps.append(f"  line {n}: {cmd}\n     (marked lint-only but the linter did not flag it)")
        else:
            agree += 1
            if "--show-all" in argv:
                verdict = "REJECT" if (s_bad or l_bad) else "ok"
                print(f"  {verdict:6} line {n}: {cmd}\n" + (f"     server: {srv_err[i]}\n" if s_bad else "")
                      + (f"     linter: {lint_err[i]}\n" if l_bad else ""), end="")
    for case in jcases:
        s_bad, l_bad = case in jsrv, case in jlint
        lint_only = "__lintonly" in case
        if s_bad and not l_bad:
            gaps.append(f"  json {case}\n     server: {jsrv[case]}")
        elif l_bad and not s_bad and not lint_only:
            fps.append(f"  json {case}\n     linter: {jlint[case]}")
        elif lint_only and not l_bad:
            gaps.append(f"  json {case}\n     (marked lint-only but the linter did not flag it)")
        else:
            agree += 1
            if "--show-all" in argv:
                print(f"  {'REJECT' if s_bad or l_bad else 'ok':6} json {case}\n"
                      + (f"     server: {jsrv[case]}\n" if s_bad else "")
                      + (f"     linter: {jlint[case]}\n" if l_bad else ""), end="")
    print(f"json corpus: {len(jcases)} files, server rejected {len(jsrv)}, linter rejected {len(jlint)}")
    print(f"corpus: {len(lines)} lines, server rejected {len(srv_err)}, linter rejected {len(lint_err)}, agree {agree}")
    if gaps:
        print(f"LINTER GAPS (server rejects / bug not flagged, linter passes): {len(gaps)}\n" + "\n".join(gaps))
    if fps:
        print(f"FALSE POSITIVES (linter rejects, server accepts): {len(fps)}\n" + "\n".join(fps))
    return 1 if gaps or fps or load_errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
