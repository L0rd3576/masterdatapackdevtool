#!/usr/bin/env python3
"""Run a datapack on a throwaway Minecraft 26.3 server and execute its tests.

Usage:
    python tools/run_tests.py <path-to-datapack> [--keep] [--skip-lint] [--only NAME]

Stages (any failure => exit code 1):
  1. lint      tools/lint_datapack.py (skip with --skip-lint)
  2. load      fresh server dir under test-server/runs/, pack copied into world/datapacks/,
               server log scanned for datapack errors (printed verbatim)
  3. tests     every <pack>/tests/*.test.json executed over RCON
Log of the run is copied to test-server/last-run.log.

Test file format: see knowledge/testing.md.
"""
import argparse
import json
import os
import re
import secrets
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_DIR = os.path.join(ROOT, "server")
SERVER_JAR = os.path.join(SERVER_DIR, "server.jar")
JAVA = os.path.join(ROOT, "runtime", "jre25", "bin", "java.exe" if os.name == "nt" else "java")
TEMPLATE_PROPS = os.path.join(ROOT, "test-server", "template", "server.properties")
RUNS_DIR = os.path.join(ROOT, "test-server", "runs")
LAST_LOG = os.path.join(ROOT, "test-server", "last-run.log")

# Gamerules applied before tests (26.3 snake_case names, verified in generated/reports/commands.json).
SETUP_COMMANDS = [
    "gamerule advance_time false",
    "gamerule advance_weather false",
    "gamerule spawn_mobs false",
    "gamerule spawn_monsters false",
    "gamerule spawn_patrols false",
    "gamerule spawn_phantoms false",
    "gamerule spawn_wandering_traders false",
    "forceload add -32 -32 31 31",
    "tick freeze",
]

# WARN lines that are environment noise, not datapack problems.
NOISE = [
    "PerfOS counters",
    "Can't keep up",
    "OFFLINE/INSECURE",
    "no attempt to authenticate",
    "hackers to connect",
    '"online-mode"',
]
# RCON responses that mean the command itself did not parse / resolve.
PARSE_ERROR = re.compile(
    r"<--\[HERE\]|^Unknown or incomplete command|^Incorrect argument|^Unknown function|"
    r"^Expected |^Invalid |^Can't find element|^Unknown (block|item|entity|effect|objective)"
)


# --------------------------------------------------------------------------- RCON
class Rcon:
    def __init__(self, port, password, timeout=30):
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        self.next_id = 1
        if self._request(3, password) is None:
            raise RuntimeError("RCON authentication failed")

    def _send(self, rid, kind, body):
        data = struct.pack("<ii", rid, kind) + body.encode("utf-8") + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(data)) + data)

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("RCON connection closed")
            buf += chunk
        return buf

    def _recv(self):
        (length,) = struct.unpack("<i", self._recv_exact(4))
        payload = self._recv_exact(length)
        rid, kind = struct.unpack("<ii", payload[:8])
        return rid, kind, payload[8:-2].decode("utf-8", "replace")

    def _request(self, kind, body):
        rid = self.next_id
        self.next_id += 1
        self._send(rid, kind, body)
        if kind == 3:
            got, _, _ = self._recv()
            return None if got == -1 else ""
        # Responses longer than 4096 bytes arrive split across packets. (A follow-up packet of an
        # unknown type makes the 26.3 server drop the connection, so read continuations by timeout.)
        _, _, text = self._recv()
        parts = [text]
        while len(parts[-1].encode("utf-8")) >= 4000:
            self.sock.settimeout(0.5)
            try:
                parts.append(self._recv()[2])
            except socket.timeout:
                break
            finally:
                self.sock.settimeout(30)
        return "".join(parts)

    def cmd(self, command):
        if len(command.encode("utf-8")) > 1446:
            raise ValueError("RCON commands are limited to 1446 bytes; put long commands in a function")
        return self._request(2, command)

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


# --------------------------------------------------------------------------- server
def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Server:
    def __init__(self, pack_dir, keep=False):
        self.pack_dir = pack_dir
        self.keep = keep
        os.makedirs(RUNS_DIR, exist_ok=True)
        self.run_dir = os.path.join(RUNS_DIR, time.strftime("run-%Y%m%d-%H%M%S-") + secrets.token_hex(2))
        self.lines = []
        self.lock = threading.Lock()
        self.proc = None
        self.rcon = None

    def prepare(self):
        os.makedirs(self.run_dir)
        self.password = secrets.token_hex(12)
        self.rcon_port = free_port()
        props = open(TEMPLATE_PROPS, encoding="utf-8").read()
        props += f"\nrcon.port={self.rcon_port}\nrcon.password={self.password}\nserver-port={free_port()}\n"
        with open(os.path.join(self.run_dir, "server.properties"), "w", encoding="utf-8") as f:
            f.write(props)
        with open(os.path.join(self.run_dir, "eula.txt"), "w") as f:
            f.write("eula=true\n")
        self.pack_name = os.path.basename(os.path.normpath(self.pack_dir))
        dest = os.path.join(self.run_dir, "world", "datapacks", self.pack_name)
        shutil.copytree(self.pack_dir, dest, ignore=shutil.ignore_patterns("tests", ".git", "*.md"))

    def _reader(self):
        for raw in self.proc.stdout:
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            with self.lock:
                self.lines.append(line)

    def start(self, timeout=180):
        cmd = [JAVA, "-Xmx2G", f"-DbundlerRepoDir={SERVER_DIR}", "-jar", SERVER_JAR, "nogui"]
        self.proc = subprocess.Popen(cmd, cwd=self.run_dir, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        threading.Thread(target=self._reader, daemon=True).start()
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self.lock:
                text = "\n".join(self.lines[-20:])
            if re.search(r"RCON running on", text):
                break
            if self.proc.poll() is not None:
                time.sleep(0.5)
                return False
            time.sleep(0.25)
        else:
            return False
        for _ in range(40):
            try:
                self.rcon = Rcon(self.rcon_port, self.password)
                return True
            except OSError:
                time.sleep(0.25)
        return False

    def log_since(self, index):
        with self.lock:
            return self.lines[index:]

    def stop(self):
        if self.rcon:
            try:
                self.rcon.cmd("stop")
            except Exception:
                pass
            self.rcon.close()
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        time.sleep(0.3)
        with self.lock:
            log = "\n".join(self.lines) + "\n"
        with open(LAST_LOG, "w", encoding="utf-8") as f:
            f.write(log)
        if not self.keep:
            shutil.rmtree(self.run_dir, ignore_errors=True)


def datapack_errors(lines):
    """Return list of error blocks (each a list of lines) found in server log lines."""
    errors = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"\[[\d:]+\] \[[^\]]*/(ERROR|WARN)\]: (.*)", line)
        if m and not any(n in line for n in NOISE):
            block = [line]
            j = i + 1
            # attach continuation lines (exception text, registry error tree) but not stack frames
            while j < len(lines) and not re.match(r"\[[\d:]+\] \[", lines[j]):
                cont = lines[j]
                if not re.match(r"\s+at |\s+\.\.\. \d+ more", cont) and cont.strip():
                    block.append(cont)
                j += 1
            if m.group(1) == "ERROR" or re.search(
                    r"pack|function|tag|registry|parse|load|Couldn't|Failed|Missing|Unknown", m.group(2), re.I):
                errors.append(block)
            i = j
        else:
            i += 1
    return errors


# --------------------------------------------------------------------------- tests
class TestFailure(Exception):
    pass


def norm(s):
    return re.sub(r"\s+", " ", s.strip())


def snbt_norm(s):
    """Drop whitespace outside quoted strings: the server prints SNBT as {a: 1, b: "x"}."""
    out, quote, i = [], None, 0
    s = s.strip()
    while i < len(s):
        c = s[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < len(s):
                out.append(s[i + 1])
                i += 1
            elif c == quote:
                quote = None
        elif c in "\"'":
            quote = c
            out.append(c)
        elif not c.isspace():
            out.append(c)
        i += 1
    return "".join(out)


def wait_ticks(server, n):
    before = gametime(server)
    server.rcon.cmd(f"tick step {n}")
    deadline = time.time() + max(10, n / 5)
    while time.time() < deadline:
        if gametime(server) >= before + n:
            return
        time.sleep(0.05)
    raise TestFailure(f"tick step {n} did not complete (gametime stuck at {gametime(server)})")


def gametime(server):
    out = server.rcon.cmd("time query gametime")
    m = re.search(r"(-?\d+)", out)
    if not m:
        raise TestFailure(f"could not read gametime: {out!r}")
    return int(m.group(1))


def run_cmd(server, command, allow_error=False):
    out = server.rcon.cmd(command)
    if not allow_error and PARSE_ERROR.search(out):
        raise TestFailure(f"command failed: {command}\n      response: {out}")
    return out


def run_step(server, step):
    if "run" in step:
        out = run_cmd(server, step["run"], step.get("allow_error", False))
        if "expect_contains" in step and step["expect_contains"] not in out:
            raise TestFailure(f"{step['run']}\n      expected output containing: {step['expect_contains']!r}\n      actual: {out!r}")
    elif "ticks" in step:
        wait_ticks(server, int(step["ticks"]))
    elif "assert" in step:
        cond = step["assert"].strip()
        if cond.startswith("execute "):
            cond = cond[len("execute "):]
        out = run_cmd(server, "execute " + cond)
        if not out.startswith("Test passed"):
            detail = ""
            if step.get("show"):
                detail = f"\n      {step['show']} -> {server.rcon.cmd(step['show'])}"
            raise TestFailure(f"assert failed: execute {cond}\n      response: {out!r}{detail}")
    elif "assert_score" in step:
        a = step["assert_score"]
        out = run_cmd(server, f"scoreboard players get {a['target']} {a['objective']}", allow_error=True)
        m = re.search(r" has (-?\d+) \[", out)
        actual = int(m.group(1)) if m else None
        if actual != a["equals"]:
            raise TestFailure(f"assert_score {a['target']} {a['objective']}: expected {a['equals']}, actual "
                              f"{actual if m else 'unset'}  (response: {out!r})")
    elif "assert_data" in step:
        a = step["assert_data"]
        cmd = f"data get {a['source']} {a.get('path', '')}".strip()
        out = run_cmd(server, cmd, allow_error=True)
        m = re.search(r"(?:contents|has the following [a-z ]*data|following entity data|following block data): (.*)$", out, re.S)
        actual = m.group(1) if m else None
        if actual is None or snbt_norm(actual) != snbt_norm(a["equals"]):
            raise TestFailure(f"assert_data {cmd}: expected {a['equals']}, actual {actual!r}  (response: {out!r})")
    elif "assert_output" in step:
        a = step["assert_output"]
        out = run_cmd(server, a["command"], allow_error=True)
        if "equals" in a and norm(out) != norm(a["equals"]):
            raise TestFailure(f"assert_output {a['command']}: expected {a['equals']!r}, actual {out!r}")
        if "contains" in a and a["contains"] not in out:
            raise TestFailure(f"assert_output {a['command']}: expected to contain {a['contains']!r}, actual {out!r}")
        if "matches" in a and not re.search(a["matches"], out):
            raise TestFailure(f"assert_output {a['command']}: expected to match /{a['matches']}/, actual {out!r}")
    else:
        raise TestFailure(f"unknown step type: {step}")


def run_test(server, path):
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    log_mark = len(server.log_since(0))
    try:
        for c in spec.get("setup", []):
            run_cmd(server, c)
        for step in spec.get("steps", []):
            run_step(server, step if isinstance(step, dict) else {"run": step})
    finally:
        for c in spec.get("teardown", []):
            try:
                server.rcon.cmd(c)
            except Exception:
                pass
    time.sleep(0.1)
    errs = datapack_errors(server.log_since(log_mark))
    if errs:
        raise TestFailure("server logged errors during test:\n" + "\n".join("      " + l for b in errs for l in b))


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack")
    ap.add_argument("--keep", action="store_true", help="keep the run directory")
    ap.add_argument("--skip-lint", action="store_true")
    ap.add_argument("--only", help="run only tests whose file name contains this")
    args = ap.parse_args()
    pack = os.path.abspath(args.pack)
    if not os.path.isfile(os.path.join(pack, "pack.mcmeta")):
        print(f"FAIL: {pack} has no pack.mcmeta")
        return 1
    for p in (JAVA, SERVER_JAR, TEMPLATE_PROPS):
        if not os.path.exists(p):
            print(f"FAIL: missing {p} (see claude-code-prompt.md phase 1)")
            return 1

    failed = []
    if not args.skip_lint:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lint_datapack.py"), pack],
                           capture_output=True, text=True)
        print("== lint: " + ("PASS" if r.returncode == 0 else "FAIL"))
        if r.returncode != 0:
            print("\n".join("   " + l for l in r.stdout.strip().splitlines()[-40:]))
            failed.append("lint")

    server = Server(pack, keep=args.keep)
    server.prepare()
    t0 = time.time()
    started = server.start()
    try:
        boot_lines = server.log_since(0)
        errs = datapack_errors(boot_lines)
        if not started:
            print("== load: FAIL (server did not start)")
            shown = [l for b in errs for l in b] or [l for l in boot_lines[-30:] if not re.match(r"\s+at ", l)]
            for l in shown[:60]:
                print("   " + l)
            failed.append("load")
            return 1
        enabled = server.rcon.cmd("datapack list enabled")
        if f"file/{server.pack_name}" not in enabled:
            errs.append([f"pack 'file/{server.pack_name}' is not enabled: {enabled}"])
        if errs:
            print(f"== load: FAIL ({len(errs)} error(s))")
            for b in errs:
                for l in b:
                    print("   " + l)
            failed.append("load")
        else:
            print(f"== load: PASS ({time.time() - t0:.1f}s)")

        for c in SETUP_COMMANDS:
            server.rcon.cmd(c)

        tests_dir = os.path.join(pack, "tests")
        tests = sorted(f for f in os.listdir(tests_dir) if f.endswith(".test.json")) if os.path.isdir(tests_dir) else []
        if args.only:
            tests = [t for t in tests if args.only in t]
        if not tests:
            print("== tests: none found (add tests/<name>.test.json)")
        passed = 0
        for t in tests:
            try:
                run_test(server, os.path.join(tests_dir, t))
                print(f"   PASS {t}")
                passed += 1
            except (TestFailure, ValueError, KeyError, json.JSONDecodeError) as e:
                print(f"   FAIL {t}\n      {e}")
                failed.append(t)
        if tests:
            print(f"== tests: {passed}/{len(tests)} passed")
    finally:
        server.stop()
        print(f"   server log: {os.path.relpath(LAST_LOG, os.getcwd()) if os.path.splitdrive(LAST_LOG)[0] == os.path.splitdrive(os.getcwd())[0] else LAST_LOG}")
    print("RESULT: " + ("FAIL (" + ", ".join(failed) + ")" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
