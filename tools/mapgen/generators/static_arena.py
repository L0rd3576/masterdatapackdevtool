"""static_arena: a walled rectangular arena with optional obstacles, spawn pads on a ring, and a centre objective.

Every number comes from params (defaults in PARAMS_SCHEMA) or the palette; nothing game-specific is hard-coded.
"""
import math

NAME = "static_arena"
DESCRIPTION = "Small fixed arena: floor, walls, random obstacle pillars (connectivity kept), spawn ring."

PARAMS_SCHEMA = {
    "type": "object",
    "properties": {
        "size": {"type": "array", "items": {"type": "integer", "minimum": 7}, "minItems": 3, "maxItems": 3,
                 "default": [25, 8, 25], "description": "[width x, height y, depth z] including walls and floor."},
        "palette": {"$ref": "common.schema.json#/definitions/palette_ref"},
        "wall_height": {"type": "integer", "minimum": 2, "default": 4},
        "floor_pattern": {"enum": ["solid", "checker", "border"], "default": "checker"},
        "obstacle_density": {"type": "number", "minimum": 0, "maximum": 0.4, "default": 0.05,
                             "description": "Fraction of inner floor cells that get a pillar."},
        "obstacle_height": {"type": "array", "items": {"type": "integer", "minimum": 1}, "minItems": 2, "maxItems": 2,
                            "default": [1, 3], "description": "[min, max] pillar height."},
        "spawn_margin": {"type": "integer", "minimum": 1, "default": 3, "description": "Spawn ring distance from the walls."},
        "spawn_clearance": {"type": "integer", "minimum": 0, "default": 1, "description": "No obstacles within this radius of a spawn."},
        "light_every": {"type": "integer", "minimum": 0, "default": 6, "description": "Light block in the wall every N blocks (0 = none)."},
        "center_objective": {"type": "boolean", "default": True},
        "roof": {"type": "boolean", "default": False}
    },
    "additionalProperties": False
}


def generate(params, rng, ctx):
    import core
    from model import Model

    w, h, d = params["size"]
    wh = params["wall_height"]
    if wh + 2 > h:
        raise core.MapgenError(f"static_arena: wall_height {wh} needs size y >= {wh + 2}")
    pal = ctx.palette
    m = Model((w, h, d))
    # floor
    for z in range(d):
        for x in range(w):
            role = "floor"
            if params["floor_pattern"] == "checker" and (x + z) % 2:
                role = "floor_alt"
            elif params["floor_pattern"] == "border" and (x in (1, w - 2) or z in (1, d - 2)):
                role = "floor_alt"
            m.set(x, 0, z, pal.get(role, fallback="floor"))
    # walls (+ lights, + top)
    m.walls((0, 1, 0), (w - 1, wh, d - 1), pal.get("wall"))
    if params["light_every"]:
        n = params["light_every"]
        ly = min(wh, 2)
        for x in range(n // 2, w, n):
            m.set(x, ly, 0, pal.get("light"))
            m.set(x, ly, d - 1, pal.get("light"))
        for z in range(n // 2, d, n):
            m.set(0, ly, z, pal.get("light"))
            m.set(w - 1, ly, z, pal.get("light"))
    if pal.has("wall_top") and wh + 1 < h:
        m.walls((0, wh + 1, 0), (w - 1, wh + 1, d - 1), pal.get("wall_top"))
    if params["roof"]:
        m.fill((0, h - 1, 0), (w - 1, h - 1, d - 1), pal.get("ceiling"))

    # spawn ring: evenly spaced along the inset rectangle
    mg = params["spawn_margin"]
    x0, z0, x1, z1 = mg, mg, w - 1 - mg, d - 1 - mg
    if x1 <= x0 or z1 <= z0:
        raise core.MapgenError("static_arena: spawn_margin too large for the size")
    ring = ([(x, z0) for x in range(x0, x1)] + [(x1, z) for z in range(z0, z1)] +
            [(x, z1) for x in range(x1, x0, -1)] + [(x0, z) for z in range(z1, z0, -1)])
    n = ctx.max_players
    spawns = []
    for i in range(n):
        x, z = ring[(i * len(ring)) // n]
        spawns.append((x, 1, z))
        m.set(x, 0, z, pal.get("spawn_pad", fallback="floor_alt"))
    markers = []
    cx, cz = w // 2, d // 2
    if params["center_objective"]:
        m.set(cx, 0, cz, pal.get("objective"))
        markers.append({"id": "center", "type": "objective", "pos": [cx, 1, cz]})

    # obstacles, skipping cells near spawns/centre; drop any that break connectivity
    clear = params["spawn_clearance"]
    keep_free = set()
    for sx, _, sz in spawns + [(cx, 1, cz)]:
        for dx in range(-clear, clear + 1):
            for dz in range(-clear, clear + 1):
                keep_free.add((sx + dx, sz + dz))
    inner = [(x, z) for z in range(2, d - 2) for x in range(2, w - 2) if (x, z) not in keep_free]
    count = int(math.floor(len(inner) * params["obstacle_density"]))
    lo, hi = params["obstacle_height"]
    placed = []
    for _ in range(count):
        if not inner:
            break
        x, z = inner.pop(rng.randint(0, len(inner) - 1))
        ph = rng.randint(lo, min(hi, wh))
        block = pal.get("obstacle", rng)
        for y in range(1, ph + 1):
            m.set(x, y, z, block)
        placed.append((x, z, ph))
        walk = core.Walk(m, ctx.config)
        reach = walk.reachable_from(spawns[0])
        if any(s not in reach for s in spawns[1:]) or (params["center_objective"] and (cx, 1, cz) not in reach):
            for y in range(1, ph + 1):
                m.clear(x, y, z)
            placed.pop()
    return {"model": m, "spawns": spawns, "markers": markers,
            "meta": {"obstacles": len(placed), "ring_cells": len(ring)}}
