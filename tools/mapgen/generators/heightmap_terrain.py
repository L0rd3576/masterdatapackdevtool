"""heightmap_terrain: natural terrain from seeded fractal value noise (tools/mapgen/noise.py).

Scaffolding for large landscapes: noise is evaluated in world coordinates (`offset` + local), so neighbouring
tiles generated with offsets that differ by the tile size line up seamlessly; place them as separate templates
(see knowledge/mapgen.md for size limits and tiling).
"""

NAME = "heightmap_terrain"
DESCRIPTION = "Noise heightmap terrain with water level, beaches, snow peaks; tileable via offset."

PARAMS_SCHEMA = {
    "type": "object",
    "properties": {
        "size": {"type": "array", "items": {"type": "integer", "minimum": 4}, "minItems": 3, "maxItems": 3,
                 "default": [64, 40, 64]},
        "offset": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2, "default": [0, 0],
                   "description": "World-space [x, z] of this tile (noise continuity across tiles)."},
        "palette": {"$ref": "common.schema.json#/definitions/palette_ref", "default": "temperate_terrain"},
        "scale": {"type": "number", "exclusiveMinimum": 0, "default": 28.0, "description": "Blocks per noise lattice cell."},
        "octaves": {"type": "integer", "minimum": 1, "maximum": 8, "default": 4},
        "lacunarity": {"type": "number", "minimum": 1, "default": 2.0},
        "gain": {"type": "number", "exclusiveMinimum": 0, "maximum": 1, "default": 0.5},
        "base_height": {"type": "integer", "minimum": 1, "default": 6},
        "amplitude": {"type": "integer", "minimum": 0, "default": 24},
        "water_level": {"type": ["integer", "null"], "default": 12, "description": "null = no water."},
        "beach_band": {"type": "integer", "minimum": 0, "default": 1, "description": "Sand up to water_level + this."},
        "peak_height": {"type": ["integer", "null"], "default": 28, "description": "Snow on surfaces at or above this y."},
        "soil_depth": {"type": "integer", "minimum": 0, "default": 3},
        "edge_falloff": {"type": "integer", "minimum": 0, "default": 0,
                         "description": "Lower the terrain over this many blocks near the edges (island look)."},
        "spawn_max_slope": {"type": "integer", "minimum": 0, "default": 1},
        "spawn_grid": {"type": "integer", "minimum": 1, "default": 4, "description": "Spacing of spawn candidate sampling."}
    },
    "additionalProperties": False
}


def generate(params, rng, ctx):
    import core
    import noise
    from model import Model

    w, h, d = params["size"]
    ox, oz = params["offset"]
    pal = ctx.palette
    m = Model((w, h, d))

    def put(x, y, z, role):
        m.set(x, y, z, pal.get(role, fallback="base"))

    seed = rng.next_u64()
    fall = params["edge_falloff"]
    heights = []
    for z in range(d):
        row = []
        for x in range(w):
            v = noise.fbm2d(seed, (ox + x) / params["scale"], (oz + z) / params["scale"], params["octaves"],
                            params["lacunarity"], params["gain"])
            if fall:
                edge = min(x, z, w - 1 - x, d - 1 - z)
                if edge < fall:
                    v *= edge / fall
            row.append(max(1, min(h - 3, params["base_height"] + int(v * params["amplitude"]))))
        heights.append(row)

    wl, peak, soil = params["water_level"], params["peak_height"], params["soil_depth"]
    for z in range(d):
        for x in range(w):
            top = heights[z][x]
            shore = wl is not None and top <= wl + params["beach_band"]
            for y in range(0, top):
                put(x, y, z, ("beach" if shore else "fill") if y >= top - soil else "deep")
            put(x, top, z, "peak" if peak is not None and top >= peak else "beach" if shore else "top")
            if wl is not None:
                for y in range(top + 1, wl + 1):
                    put(x, y, z, "water")

    # spawn candidates: flat-enough sampled columns, restricted to the largest connected walkable region
    walk = core.Walk(m, ctx.config)
    g = params["spawn_grid"]
    cands = []
    for z in range(g // 2, d, g):
        for x in range(g // 2, w, g):
            top = heights[z][x]
            nb = [heights[zz][xx] for xx, zz in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1))
                  if 0 <= xx < w and 0 <= zz < d]
            if nb and max(abs(top - v) for v in nb) <= params["spawn_max_slope"] and walk.standable(x, top + 1, z):
                cands.append((x, top + 1, z))
    best, pool = [], list(cands)
    while pool:
        reach = walk.reachable_from(pool[0])
        group = [c for c in pool if c in reach]
        pool = [c for c in pool if c not in reach]
        if len(group) > len(best):
            best = group
    hs = [v for row in heights for v in row]
    return {"model": m, "spawns": best, "markers": [],
            "meta": {"min_height": min(hs), "max_height": max(hs), "spawn_candidates": len(cands)}}
