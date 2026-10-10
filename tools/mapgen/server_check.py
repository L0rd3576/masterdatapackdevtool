"""Load maps on a throwaway 26.3 server (via tools/run_tests.py's Server) and read blocks back.

MapServer builds a probe pack (arena void dimension + one structure per map), boots once, and check_map()
places a map with `place template`, then verifies a deterministic sample of blocks with `execute if block`.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import run_tests as rt  # noqa: E402

import pipeline  # noqa: E402
import rng as rngmod  # noqa: E402

NS = "mapcheck"


class MapServer:
    def __init__(self, results, config):
        self.results, self.cfg = results, config
        self.pack = os.path.join(rt.ROOT, "test-server", "mapgen-probe-pack")
        self.server = None
        self.slots = {}
        x = 0
        for r in results:
            self.slots[r.manifest["id"]] = x
            x += r.model.size[0] + 32

    def _write_pack(self):
        if os.path.isdir(self.pack):
            shutil.rmtree(self.pack)
        os.makedirs(os.path.join(self.pack, "data", NS, "structure"))
        os.makedirs(os.path.join(self.pack, "data", NS, "dimension"))
        with open(os.path.join(self.pack, "pack.mcmeta"), "w") as f:
            f.write('{"pack":{"description":"mapgen server check","min_format":121,"max_format":121}}\n')
        with open(os.path.join(self.pack, "data", NS, "dimension", "arena.json"), "w") as f:
            f.write('{"type":"minecraft:overworld","generator":{"type":"minecraft:flat","settings":'
                    '{"biome":"minecraft:the_void","features":false,"lakes":false,"layers":[]}}}\n')
        for r in self.results:
            with open(os.path.join(self.pack, "data", NS, "structure", r.manifest["id"] + ".nbt"), "wb") as f:
                f.write(pipeline.structure_bytes(r.model, self.cfg))

    def start(self):
        self._write_pack()
        self.server = rt.Server(self.pack)
        self.server.prepare()
        if not self.server.start(timeout=self.cfg.get("server_check", {}).get("boot_timeout_seconds", 180)):
            errs = rt.datapack_errors(self.server.log_since(0))
            self.stop()
            raise RuntimeError("server did not start: " + " | ".join(l for b in errs for l in b)[:800])
        errs = rt.datapack_errors(self.server.log_since(0))
        if errs:
            self.stop()
            raise RuntimeError("load errors: " + " | ".join(l for b in errs for l in b)[:800])

    def cmd(self, c):
        return self.server.rcon.cmd(c)

    def check_map(self, result, config):
        mid = result.manifest["id"]
        x0, y0, z0 = self.slots[mid], 64, 0
        sx, sy, sz = result.model.size
        mark = len(self.server.log_since(0))
        out = []
        self.cmd(f"execute in {NS}:arena run forceload add {x0} {z0} {x0 + sx - 1} {z0 + sz - 1}")
        t = time.time()
        resp = self.cmd(f"execute in {NS}:arena run place template {NS}:{mid} {x0} {y0} {z0}")
        ms = (time.time() - t) * 1000
        if "Loaded template" not in resp:
            return [("ERROR", f"place template failed: {resp!r}")]
        # deterministic sample: corners, spawns' ground, then random set cells and random untouched cells
        r = rngmod.Rng("server-check:" + mid)
        keys = sorted(result.model.blocks)
        n = config.get("server_check", {}).get("sample_blocks", 48)
        cells = [(0, 0, 0), (sx - 1, sy - 1, sz - 1), (sx - 1, 0, 0), (0, 0, sz - 1)]
        cells += [(x, y - 1, z) for x, y, z in result.spawns[:8]]
        cells += [result.model.unkey(keys[r.randint(0, len(keys) - 1)]) for _ in range(n)] if keys else []
        cells += [(r.randint(0, sx - 1), r.randint(0, sy - 1), r.randint(0, sz - 1)) for _ in range(n // 4)]
        bad = []
        fill_air = config["structure"]["fill_air"]
        for (x, y, z) in cells:
            st = result.model.get(x, y, z)
            if st is None:
                if not fill_air:
                    continue
                st = "minecraft:air"
            resp = self.cmd(f"execute in {NS}:arena if block {x0 + x} {y0 + y} {z0 + z} {st}")
            if not resp.startswith("Test passed"):
                actual = self.cmd(f"execute in {NS}:arena run data get block {x0 + x} {y0 + y} {z0 + z}")
                bad.append(f"({x},{y},{z}) expected {st}: {resp!r} {actual[:80]!r}")
        errs = rt.datapack_errors(self.server.log_since(mark))
        if errs:
            out.append(("ERROR", "server logged: " + " | ".join(l for b in errs for l in b)[:600]))
        if bad:
            out.append(("ERROR", f"{len(bad)}/{len(cells)} sampled blocks differ: " + "; ".join(bad[:3])))
        if not out:
            out.append(("INFO", f"placed in {ms:.0f} ms (RCON round trip incl.), {len(cells)} sampled blocks match"))
        return out

    def stop(self):
        if self.server:
            self.server.stop()
            self.server = None
