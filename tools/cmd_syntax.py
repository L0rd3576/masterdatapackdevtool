#!/usr/bin/env python3
"""Print the 26.3 command grammar from generated/reports/commands.json.

Usage:
    python tools/cmd_syntax.py scoreboard            # all usage paths of /scoreboard
    python tools/cmd_syntax.py execute if            # paths starting with "execute if"
    python tools/cmd_syntax.py --depth 3 data        # limit depth
    python tools/cmd_syntax.py --parsers             # list argument parser types

Notation: literal words as-is, <name:parser{props}> arguments, [exec] = command can end here,
-> X = redirects to X (e.g. execute subcommands chain back to "execute").
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "generated", "reports", "commands.json")


def label(name, node):
    if node["type"] == "literal":
        return name
    props = node.get("properties")
    p = node["parser"].replace("minecraft:", "").replace("brigadier:", "")
    if props:
        p += "{" + ",".join(f"{k}={v}" for k, v in props.items()) + "}"
    return f"<{name}:{p}>"


def walk(node, prefix, depth, out):
    children = node.get("children", {})
    if node.get("executable"):
        out.append(" ".join(prefix) + "  [exec]")
    if "redirect" in node:
        out.append(" ".join(prefix) + "  -> " + " ".join(node["redirect"]))
    elif not children and not node.get("executable") and prefix:
        out.append(" ".join(prefix) + "  -> <any command>")
    if depth == 0:
        if children:
            out.append(" ".join(prefix) + " ...")
        return
    for name, child in children.items():
        walk(child, prefix + [label(name, child)], depth - 1, out)


def main(argv):
    tree = json.load(open(REPORT, encoding="utf-8"))
    depth = 99
    if "--depth" in argv:
        i = argv.index("--depth")
        depth = int(argv[i + 1])
        del argv[i:i + 2]
    if "--parsers" in argv:
        found = set()

        def rec(n):
            if n.get("type") == "argument":
                found.add(n["parser"])
            for c in n.get("children", {}).values():
                rec(c)
        rec(tree)
        print("\n".join(sorted(found)))
        return 0
    if not argv:
        print(" ".join(sorted(tree["children"])))
        return 0
    node, prefix = tree, []
    for word in argv:
        kids = node.get("children", {})
        if word in kids:
            node = kids[word]
            prefix.append(label(word, node))
        else:
            print(f"'{word}' is not a literal child of '{' '.join(prefix) or '<root>'}'. Options: "
                  + " ".join(label(k, v) for k, v in kids.items()))
            return 1
    out = []
    walk(node, prefix, depth, out)
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
