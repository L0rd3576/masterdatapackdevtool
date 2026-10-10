#!/usr/bin/env python3
"""Create a new 26.3 datapack from template-datapack/ with the tested function library vendored in.

Usage:
    python tools/new_project.py <namespace> <dest-pack-dir> [--lib-prefix PREFIX] [--no-lib]
    python tools/new_project.py --update <pack-dir> [--lib-prefix PREFIX]     (re-vendor the current library)

- <namespace>: your pack's namespace (a-z 0-9 _ - .); replaces `example` from the template.
- The library (library/mcdp_lib/data/mcdp_lib, without its tests and test helpers) is copied to
  data/<PREFIX>/ (default mcdp_lib); with --lib-prefix every `mcdp_lib` identifier (functions, objectives,
  storages, tags) is renamed so two packs with different library versions cannot clash.
- #minecraft:load / #minecraft:tick list the library first, then your functions.
Afterwards: python tools/lint_datapack.py <dest> && python tools/run_tests.py <dest>
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "template-datapack")
LIB = os.path.join(ROOT, "library", "mcdp_lib")
NS_RE = re.compile(r"[a-z0-9_.\-]+")


def rewrite_tree(root, pattern, repl):
    for dp, _, fns in os.walk(root):
        for fn in fns:
            p = os.path.join(dp, fn)
            if not fn.endswith((".mcfunction", ".json", ".mcmeta", ".md")):
                continue
            text = open(p, encoding="utf-8").read()
            new = re.sub(pattern, repl, text)
            if new != text:
                with open(p, "w", encoding="utf-8", newline="\n") as f:
                    f.write(new)


def set_tag(pack, tag, first, ours):
    p = os.path.join(pack, "data", "minecraft", "tags", "function", tag + ".json")
    values = json.load(open(p, encoding="utf-8"))["values"] if os.path.exists(p) else []
    values = [v for v in values if not (isinstance(v, str) and v.endswith(":_internal/" + tag))]
    if first:
        values.insert(0, first)
    if ours and ours not in values:
        values.append(ours)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"values": values}, f, indent=2)
        f.write("\n")


def vendor(pack, prefix):
    dest = os.path.join(pack, "data", prefix)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(os.path.join(LIB, "data", "mcdp_lib"), dest)
    if prefix != "mcdp_lib":
        rewrite_tree(dest, r"\bmcdp_lib(?=[:. ])", prefix)
    set_tag(pack, "load", f"{prefix}:_internal/load", None)
    set_tag(pack, "tick", f"{prefix}:_internal/tick", None)


def main(argv):
    prefix = "mcdp_lib"
    if "--lib-prefix" in argv:
        i = argv.index("--lib-prefix")
        prefix = argv[i + 1]
        del argv[i:i + 2]
    if not NS_RE.fullmatch(prefix):
        print(f"FAIL: invalid --lib-prefix '{prefix}'")
        return 1
    if argv[:1] == ["--update"] and len(argv) == 2:
        pack = os.path.abspath(argv[1])
        if not os.path.isfile(os.path.join(pack, "pack.mcmeta")):
            print(f"FAIL: {pack} is not a datapack")
            return 1
        vendor(pack, prefix)
        print(f"updated data/{prefix} in {pack} from library/mcdp_lib")
        return 0
    no_lib = "--no-lib" in argv
    argv = [a for a in argv if a != "--no-lib"]
    if len(argv) != 2:
        print(__doc__)
        return 1
    ns, pack = argv[0], os.path.abspath(argv[1])
    if not NS_RE.fullmatch(ns) or ns in ("minecraft", prefix):
        print(f"FAIL: invalid namespace '{ns}' (a-z 0-9 _ - ., not minecraft or the library prefix)")
        return 1
    if os.path.exists(pack) and os.listdir(pack):
        print(f"FAIL: {pack} exists and is not empty")
        return 1
    shutil.copytree(TEMPLATE, pack, dirs_exist_ok=True)
    os.rename(os.path.join(pack, "data", "example"), os.path.join(pack, "data", ns))
    rewrite_tree(pack, r"\bexample(?=[:.])", ns)
    meta = os.path.join(pack, "pack.mcmeta")
    m = json.load(open(meta, encoding="utf-8"))
    m["pack"]["description"] = f"{ns} (Minecraft Java 26.3)"
    with open(meta, "w", encoding="utf-8", newline="\n") as f:
        json.dump(m, f, indent=2)
        f.write("\n")
    if not no_lib:
        vendor(pack, prefix)
        with open(os.path.join(pack, "tests", "library.test.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({
                "description": f"the vendored library ({prefix}) loads and works inside this pack",
                "setup": [f"scoreboard objectives add {ns}.t dummy"],
                "steps": [
                    {"run": f"scoreboard players set #a {prefix}.in 3"},
                    {"run": f"scoreboard players set #b {prefix}.in 9"},
                    {"run": f"execute store result score #max {ns}.t run function {prefix}:math/max"},
                    {"assert_score": {"target": "#max", "objective": f"{ns}.t", "equals": 9}},
                    {"run": f"function {prefix}:score/counter_global {{objective:\"{ns}.rounds\",amount:2}}"},
                    {"assert_score": {"target": "#global", "objective": f"{ns}.rounds", "equals": 2}},
                ]}, f, indent=2)
            f.write("\n")
    with open(os.path.join(pack, "CLAUDE.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {ns} datapack (Minecraft Java 26.3, format 121)\n\n"
                f"- Own code: `data/{ns}/`. Lint: `python C:/Users/lrafy/mc-datapack-tools/tools/lint_datapack.py <this dir>`;"
                f" test: `.../tools/run_tests.py <this dir>` (tests in `tests/`).\n")
        if not no_lib:
            f.write(f"- `data/{prefix}/` is the vendored mcdp_lib library: do not edit it here. Before writing a helper, search"
                    f" `C:/Users/lrafy/mc-datapack-tools/library/INDEX.md` (names there use `mcdp_lib:`; here use `{prefix}:`)."
                    f" Update with `python .../tools/new_project.py --update <this dir>"
                    f"{' --lib-prefix ' + prefix if prefix != 'mcdp_lib' else ''}`.\n")
    print(f"created {pack} (namespace {ns}{'' if no_lib else ', library as ' + prefix})")
    print(f"next: python tools/lint_datapack.py \"{pack}\" && python tools/run_tests.py \"{pack}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
