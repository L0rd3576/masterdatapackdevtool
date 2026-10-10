#!/usr/bin/env python3
"""Render a map model: top-down PNG, per-layer contact sheet PNG, single-layer PNGs and ASCII layer dumps.
PNGs are written with stdlib zlib/struct. Colors come from config.json render.colors (exact id or glob);
unknown blocks get a stable hash color. North (-z) is up, east (+x) is right.

Usage:
    python tools/mapgen/render.py <maps/<id>.json> [--out DIR] [--layer Y ...] [--ascii] [--project-dir DIR]
"""
import argparse
import fnmatch
import hashlib
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TRANSPARENT = ("minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:structure_void")


def write_png(path, width, height, pixels):
    """pixels: list of rows, each a bytearray of RGB triples."""
    raw = b"".join(b"\x00" + bytes(row) for row in pixels)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def hex_rgb(h):
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


class Colors:
    def __init__(self, cfg):
        self.exact = {k: hex_rgb(v) for k, v in cfg["render"]["colors"].items() if "*" not in k}
        self.globs = [(k, hex_rgb(v)) for k, v in cfg["render"]["colors"].items() if "*" in k]
        self.cache = {}

    def of(self, name):
        c = self.cache.get(name)
        if c is None:
            c = self.exact.get(name)
            if c is None:
                c = next((v for k, v in self.globs if fnmatch.fnmatchcase(name, k)), None)
            if c is None:
                h = hashlib.md5(name.encode()).digest()
                c = (64 + h[0] % 160, 64 + h[1] % 160, 64 + h[2] % 160)
            self.cache[name] = c
        return c


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.rows = [bytearray(bg * w) for _ in range(h)]

    def rect(self, x0, y0, x1, y1, rgb):
        for y in range(max(0, y0), min(self.h, y1)):
            row = self.rows[y]
            for x in range(max(0, x0), min(self.w, x1)):
                row[3 * x:3 * x + 3] = bytes(rgb)

    def save(self, path):
        write_png(path, self.w, self.h, self.rows)


def _shade(rgb, f):
    return tuple(max(0, min(255, int(c * f))) for c in rgb)


def _markers(cv, result, cfg, s, layer=None, ox=0, oy=0):
    mk = cfg["render"]["markers"]
    pts = [(p, hex_rgb(mk["spawn"]), "spawn") for p in result.spawns]
    pts += [(m["pos"], hex_rgb(mk.get(m.get("type", "other"), mk["other"])), "marker") for m in result.markers]
    for (x, y, z), rgb, kind in pts:
        if layer is not None and y != layer:
            continue
        px, pz = ox + x * s, oy + z * s
        pad = max(1, s // 5)
        cv.rect(px, pz, px + s, pz + s, (0, 0, 0))
        if kind == "spawn":
            cv.rect(px + pad, pz + pad, px + s - pad, pz + s - pad, rgb)
        else:  # diamond-ish: cross
            cv.rect(px + s // 2 - pad, pz, px + s // 2 + pad + 1, pz + s, rgb)
            cv.rect(px, pz + s // 2 - pad, px + s, pz + s // 2 + pad + 1, rgb)


def top_down(result, cfg, path):
    m, r = result.model, cfg["render"]
    s = r["scale"]
    sx, sy, sz = m.size
    colors = Colors(cfg)
    cv = Canvas(sx * s, sz * s, hex_rgb(r["background"]))
    for z in range(sz):
        for x in range(sx):
            top = None
            for y in range(sy - 1, -1, -1):
                st = m.get(x, y, z)
                if st is not None and st.split("[", 1)[0] not in TRANSPARENT:
                    top = (y, st.split("[", 1)[0])
                    break
            if top is None:
                rgb = hex_rgb(r["untouched"])
            else:
                rgb = colors.of(top[1])
                if r.get("shade_by_height", True) and sy > 1:
                    rgb = _shade(rgb, 0.55 + 0.45 * top[0] / (sy - 1))
            cv.rect(x * s, z * s, x * s + s, z * s + s, rgb)
    g = r.get("grid_every", 0)
    if g:
        gc = hex_rgb(r["grid_color"])
        for x in range(0, sx, g):
            cv.rect(x * s, 0, x * s + 1, sz * s, gc)
        for z in range(0, sz, g):
            cv.rect(0, z * s, sx * s, z * s + 1, gc)
    _markers(cv, result, cfg, s)
    cv.save(path)
    return path


def layer_png(result, cfg, y, path, cv=None, ox=0, oy=0):
    m, r = result.model, cfg["render"]
    s = r.get("layer_scale", r["scale"])
    sx, _, sz = m.size
    colors = Colors(cfg)
    own = cv is None
    if own:
        cv = Canvas(sx * s, sz * s, hex_rgb(r["background"]))
    for z in range(sz):
        for x in range(sx):
            st = m.get(x, y, z)
            if st is None:
                rgb = hex_rgb(r["untouched"])
            else:
                n = st.split("[", 1)[0]
                rgb = hex_rgb(r["air"]) if n in TRANSPARENT else colors.of(n)
            cv.rect(ox + x * s, oy + z * s, ox + x * s + s, oy + z * s + s, rgb)
    _markers(cv, result, cfg, s, layer=y, ox=ox, oy=oy)
    if own:
        cv.save(path)
    return path


def layer_sheet(result, cfg, path, layers=None):
    """All (or the given) y layers side by side, bottom layer first, 4px gaps; layers that are completely
    untouched/air are skipped."""
    m, r = result.model, cfg["render"]
    s = r.get("layer_scale", r["scale"])
    sx, sy, sz = m.size
    ys = layers if layers is not None else [
        y for y in range(sy)
        if any(m.get(x, y, z) is not None and m.get(x, y, z).split("[", 1)[0] not in TRANSPARENT
               for x in range(sx) for z in range(sz))]
    if not ys:
        ys = [0]
    cols = min(len(ys), max(1, 1600 // (sx * s + 4)))
    rows = -(-len(ys) // cols)
    cv = Canvas(cols * (sx * s + 4), rows * (sz * s + 4), (255, 255, 255))
    for i, y in enumerate(ys):
        layer_png(result, cfg, y, None, cv, (i % cols) * (sx * s + 4), (i // cols) * (sz * s + 4))
    cv.save(path)
    return path, ys


def ascii_layers(result, cfg, layers=None):
    m, a = result.model, cfg["ascii"]
    sx, sy, sz = m.size
    lines = []
    spawns = {tuple(p) for p in result.spawns}
    marks = {tuple(mk["pos"]) for mk in result.markers}
    for y in (layers if layers is not None else range(sy)):
        lines.append(f"y={y}")
        for z in range(sz):
            row = []
            for x in range(sx):
                if (x, y, z) in spawns:
                    row.append(a["spawn"])
                elif (x, y, z) in marks:
                    row.append(a["objective"])
                else:
                    st = m.get(x, y, z)
                    if st is None:
                        row.append(a["untouched"])
                    else:
                        row.append(a["chars"].get(st.split("[", 1)[0], a["default"]))
            lines.append("".join(row))
    return "\n".join(lines)


def render_all(result, cfg, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    mid = result.manifest["id"]
    paths = [top_down(result, cfg, os.path.join(out_dir, f"{mid}.top.png"))]
    p, _ = layer_sheet(result, cfg, os.path.join(out_dir, f"{mid}.layers.png"))
    paths.append(p)
    txt = os.path.join(out_dir, f"{mid}.layers.txt")
    with open(txt, "w", encoding="utf-8") as f:
        f.write(ascii_layers(result, cfg) + "\n")
    paths.append(txt)
    return paths


def main():
    import core
    import pipeline
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("--out")
    ap.add_argument("--project-dir")
    ap.add_argument("--layer", type=int, action="append")
    ap.add_argument("--ascii", action="store_true", help="print ASCII layers (all, or --layer ones)")
    args = ap.parse_args()
    try:
        cfg = core.load_config()
        man, res = pipeline.load_map(args.manifest, cfg, args.project_dir)
    except core.MapgenError as e:
        print(e)
        return 1
    out = args.out or os.path.join(core.ROOT, cfg["output_dir"])
    for p in render_all(res, cfg, out):
        print(f"wrote {p}")
    for y in args.layer or []:
        name = "%s.y%d.png" % (man["id"], y)
        print(f"wrote {layer_png(res, cfg, y, os.path.join(out, name))}")
    if args.ascii:
        print(ascii_layers(res, cfg, args.layer))
    return 0


if __name__ == "__main__":
    sys.exit(main())
