"""circle_arena: a round floor disk with an optional lava ring at its outer edge, an optional closed wall ring,
floor rings, spawn pads on a circle, and centre/view markers. Uses no randomness (output depends only on params).

Lava is always minecraft:lava: game logic (shrink zone, lava contact checks) tests for that exact block.
"""
import math

NAME = "circle_arena"
DESCRIPTION = "Round arena: floor disk, optional outer lava ring (2-layer floor), optional closed wall ring, spawn circle."

LAVA = "minecraft:lava"

PARAMS_SCHEMA = {
    "type": "object",
    "properties": {
        "radius": {"type": "integer", "minimum": 3, "default": 12,
                   "description": "Playable disk radius incl. the lava ring (cells with dx*dx + dz*dz <= radius^2)."},
        "lava_width": {"type": "integer", "minimum": 0, "default": 0,
                       "description": "Outer ring of the disk whose top floor layer is lava."},
        "floor_layers": {"type": "integer", "minimum": 1, "maximum": 2, "default": 1,
                         "description": "2 = solid base layer under the floor; required when lava_width > 0."},
        "wall_height": {"type": "integer", "minimum": 0, "default": 0,
                        "description": "Wall blocks above the floor top; 0 = no wall."},
        "wall_thickness": {"type": "integer", "minimum": 1, "default": 1,
                           "description": "8-neighbour dilation steps of the wall ring."},
        "headroom": {"type": "integer", "minimum": 2, "default": 3,
                     "description": "Air rows above the floor top when there is no wall (model height)."},
        "ring_every": {"type": "integer", "minimum": 0, "default": 3,
                       "description": "floor_alt on every n-th ring (floor(d) % n == 0); 0 = plain floor."},
        "spawn_count": {"type": "integer", "minimum": 1, "default": 16,
                        "description": "Candidate spawns on the spawn circle."},
        "spawn_radius": {"type": "integer", "minimum": 0, "default": 0,
                         "description": "Spawn circle radius; 0 = round(0.6 x (radius - lava_width))."},
        "palette": {"$ref": "common.schema.json#/definitions/palette_ref"},
        "light_every": {"type": "integer", "minimum": 0, "default": 0,
                        "description": "A light block in the inner wall ring every n cells, at floor top + 2 (0 = none)."}
    },
    "additionalProperties": False
}

_N8 = [(dx, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dz]


def generate(params, rng, ctx):
    import core
    from model import Model

    r, lw, fl = params["radius"], params["lava_width"], params["floor_layers"]
    wh, wt = params["wall_height"], params["wall_thickness"]
    if lw > 0 and fl != 2:
        raise core.MapgenError("circle_arena: lava_width > 0 needs floor_layers 2 (lava over air falls into the void)")
    if lw >= r:
        raise core.MapgenError(f"circle_arena: lava_width {lw} must be smaller than radius {r}")
    if params["light_every"] and wh < 2:
        raise core.MapgenError("circle_arena: light_every needs wall_height >= 2 (lights sit at floor top + 2)")
    inner = r - lw
    ft = fl - 1
    W = r + (wt if wh > 0 else 0)
    size = (2 * W + 1, ft + 1 + max(wh, params["headroom"]), 2 * W + 1)
    pal = ctx.palette
    m = Model(size)

    disk = [(x, z) for z in range(size[2]) for x in range(size[0]) if (x - W) ** 2 + (z - W) ** 2 <= r * r]
    disk_set = set(disk)

    # spawns: evenly spaced angles on the spawn circle, rounded to cells, deduped (order kept)
    sr = params["spawn_radius"] or round(0.6 * inner)
    n = params["spawn_count"]
    pads = []
    for i in range(n):
        a = 2 * math.pi * i / n
        c = (W + round(sr * math.cos(a)), W + round(sr * math.sin(a)))
        if c not in pads:
            pads.append(c)
    for x, z in pads:
        if (x - W) ** 2 + (z - W) ** 2 > inner * inner:
            raise core.MapgenError(f"circle_arena: spawn {[x, ft + 1, z]} is outside the inner disk "
                                   f"(spawn_radius {sr}, inner radius {inner})")
    pad_set = set(pads)

    # floor: base layer, then top layer (lava outside the inner disk, floor rings, spawn pads)
    lava_cells = 0
    for x, z in disk:
        d2 = (x - W) ** 2 + (z - W) ** 2
        if fl == 2:
            m.set(x, 0, z, pal.get("base"))
        if d2 > inner * inner:
            m.set(x, ft, z, LAVA)
            lava_cells += 1
        elif (x, z) in pad_set:
            m.set(x, ft, z, pal.get("spawn_pad"))
        elif params["ring_every"] and math.isqrt(d2) % params["ring_every"] == 0:
            m.set(x, ft, z, pal.get("floor_alt"))
        else:
            m.set(x, ft, z, pal.get("floor"))

    # wall: wall_thickness rings of cells 8-adjacent to the disk (closes diagonal gaps), y 0..ft+wall_height
    if wh > 0:
        filled, rings = set(disk_set), []
        for _ in range(wt):
            ring = sorted({(x + dx, z + dz) for x, z in filled for dx, dz in _N8} - filled)
            rings.append(ring)
            filled.update(ring)
        for ring in rings:
            for x, z in ring:
                m.fill((x, 0, z), (x, ft + wh, z), pal.get("wall"))
        if params["light_every"]:
            first = sorted(rings[0], key=lambda c: (math.atan2(c[1] - W, c[0] - W), c[0], c[1]))
            for i, (x, z) in enumerate(first):
                if i % params["light_every"] == 0:
                    m.set(x, ft + 2, z, pal.get("light"))

    spawns = [(x, ft + 1, z) for x, z in pads]
    markers = [{"id": "center", "type": "other", "pos": [W, ft, W], "reachable": False},
               {"id": "view", "type": "other", "pos": [W, ft + 8, W], "reachable": False}]
    return {"model": m, "spawns": spawns, "markers": markers,
            "meta": {"disk_cells": len(disk), "lava_cells": lava_cells, "inner_radius": inner}}
