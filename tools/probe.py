#!/usr/bin/env python3
"""Boot a throwaway 26.3 server (optionally with a datapack) and print the raw response to each command.
Research tool: use it to learn what the server really does before writing knowledge/ or library code.

Usage:
    python tools/probe.py [--pack DIR] [--file CMDS.txt] [--log] [command ...]

Commands come from --file (one per line, '#' comments skipped) and/or the arguments.
Special lines: `@ticks N` steps N game ticks (the world is frozen like in run_tests.py),
`@sleep S` waits S seconds. With --log, every new server log line after each command is printed too
(ERROR/WARN lines are always printed).
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_tests as rt  # noqa: E402

EMPTY_PACK = os.path.join(rt.ROOT, "test-server", "probe-empty-pack")


def empty_pack():
    os.makedirs(os.path.join(EMPTY_PACK, "data"), exist_ok=True)
    with open(os.path.join(EMPTY_PACK, "pack.mcmeta"), "w") as f:
        f.write('{"pack":{"description":"probe","min_format":121,"max_format":121}}')
    return EMPTY_PACK


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack")
    ap.add_argument("--file")
    ap.add_argument("--log", action="store_true", help="print all new log lines after each command")
    ap.add_argument("commands", nargs="*")
    a = ap.parse_args()
    cmds = []
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            cmds += [l.rstrip("\n") for l in f if l.strip() and not l.lstrip().startswith("#")]
    cmds += a.commands
    server = rt.Server(os.path.abspath(a.pack) if a.pack else empty_pack())
    server.prepare()
    if not server.start():
        print("server did not start; tail of log:")
        print("\n".join(server.log_since(0)[-30:]))
        server.stop()
        return 1
    try:
        for b in rt.datapack_errors(server.log_since(0)):
            print("LOAD: " + "\n      ".join(b))
        for c in rt.SETUP_COMMANDS:
            server.rcon.cmd(c)
        for c in cmds:
            mark = len(server.log_since(0))
            if c.startswith("@ticks "):
                t0 = time.time()
                rt.wait_ticks(server, int(c.split()[1]))
                out = f"(stepped {c.split()[1]} ticks in {time.time() - t0:.2f}s)"
            elif c.startswith("@sleep "):
                time.sleep(float(c.split()[1]))
                out = ""
            else:
                t0 = time.time()
                out = server.rcon.cmd(c)
                out += f"   [{(time.time() - t0) * 1000:.0f} ms]"
            print(f"> {c}\n  {out}")
            time.sleep(0.05)
            for l in server.log_since(mark):
                if a.log or "/ERROR]" in l or "/WARN]" in l:
                    print("  | " + l[:400])
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
