"""room_grid: a grid of walled rooms joined by corridors along a random spanning tree (always connected),
plus optional extra loops. Room interiors come from a weighted piece library (built-in pieces and/or structure
files stamped with a random rotation)."""

NAME = "room_grid"
DESCRIPTION = "Grid of rooms and corridors from a piece library; connectivity guaranteed by a spanning tree."

PARAMS_SCHEMA = {
    "type": "object",
    "properties": {
        "grid": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 16}, "minItems": 2, "maxItems": 2,
                 "default": [3, 3], "description": "[columns along x, rows along z]."},
        "room_size": {"type": "array", "items": {"type": "integer", "minimum": 3}, "minItems": 2, "maxItems": 2,
                      "default": [7, 7], "description": "Interior [x, z] of each room (odd sizes centre doors)."},
        "wall_height": {"type": "integer", "minimum": 2, "default": 4},
        "door_height": {"type": "integer", "minimum": 2, "default": 3},
        "corridor_width": {"type": "integer", "minimum": 1, "default": 3},
        "corridor_length": {"type": "integer", "minimum": 0, "default": 3},
        "loop_chance": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.2,
                        "description": "Chance to open each non-tree connection (more loops = fewer dead ends)."},
        "roof": {"type": "boolean", "default": False},
        "palette": {"$ref": "common.schema.json#/definitions/palette_ref"},
        "pieces": {
            "type": "array", "minItems": 1,
            "default": [{"type": "builtin", "name": "empty", "weight": 3},
                        {"type": "builtin", "name": "pillars", "weight": 2},
                        {"type": "builtin", "name": "center_block", "weight": 2},
                        {"type": "builtin", "name": "planter", "weight": 1}],
            "items": {
                "type": "object", "required": ["type"],
                "properties": {
                    "type": {"enum": ["builtin", "structure"]},
                    "name": {"enum": ["empty", "pillars", "center_block", "planter"]},
                    "path": {"type": "string", "description": "Structure file relative to the project dir (type structure)."},
                    "weight": {"type": "number", "minimum": 0, "default": 1}
                },
                "additionalProperties": False
            }
        },
        "objective_rooms": {"type": "integer", "minimum": 0, "default": 1,
                            "description": "Rooms (farthest from the first spawn room first) that get an objective block."}
    },
    "additionalProperties": False
}


def _builtin(name, m, pal, rng, x0, z0, rw, rd, wh):
    """Fill a room interior (x0..x0+rw-1, z0..z0+rd-1); keep a 1-cell walkway along the walls."""
    cx, cz = x0 + rw // 2, z0 + rd // 2
    if name == "pillars" and rw >= 5 and rd >= 5:
        for px, pz in ((x0 + 1, z0 + 1), (x0 + rw - 2, z0 + 1), (x0 + 1, z0 + rd - 2), (x0 + rw - 2, z0 + rd - 2)):
            for y in range(1, wh + 1):
                m.set(px, y, pz, pal.get("accent"))
    elif name == "center_block" and rw >= 5 and rd >= 5:
        m.set(cx, 1, cz, pal.get("obstacle", rng))
    elif name == "planter" and rw >= 5 and rd >= 5:
        m.fill((cx - 1, 1, cz - 1), (cx + 1, 1, cz + 1), pal.get("obstacle", rng))
    return (cx, cz)


def generate(params, rng, ctx):
    import os
    import core
    import structure_writer
    from model import Model

    cols, rows = params["grid"]
    rw, rd = params["room_size"]
    wh, dh = params["wall_height"], min(params["door_height"], params["wall_height"])
    cw, cl = params["corridor_width"], params["corridor_length"]
    if cw > min(rw, rd):
        raise core.MapgenError("room_grid: corridor_width must not exceed the room size")
    pal = ctx.palette
    pitch_x, pitch_z = rw + 2 + cl, rd + 2 + cl
    w = cols * (rw + 2) + (cols - 1) * cl
    d = rows * (rd + 2) + (rows - 1) * cl
    h = wh + (2 if params["roof"] else 1)
    m = Model((w, h, d))

    def room_box(c, r):
        x0, z0 = c * pitch_x, r * pitch_z
        return x0, z0, x0 + rw + 1, z0 + rd + 1

    # rooms: floor + walls
    for r in range(rows):
        for c in range(cols):
            x0, z0, x1, z1 = room_box(c, r)
            m.fill((x0, 0, z0), (x1, 0, z1), pal.get("floor"))
            m.walls((x0, 1, z0), (x1, wh, z1), pal.get("wall"))
            m.set(x0 + 1 + rw // 2, 0, z0 + 1 + rd // 2, pal.get("floor_alt", fallback="floor"))
            if params["roof"]:
                m.fill((x0, wh + 1, z0), (x1, wh + 1, z1), pal.get("ceiling"))

    # spanning tree (randomized DFS) + extra loops
    edges_all = []
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                edges_all.append(((c, r), (c + 1, r)))
            if r + 1 < rows:
                edges_all.append(((c, r), (c, r + 1)))
    seen, stack, tree = {(0, 0)}, [(0, 0)], set()
    while stack:
        c, r = stack[-1]
        nbrs = [(c + dc, r + dr) for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if 0 <= c + dc < cols and 0 <= r + dr < rows and (c + dc, r + dr) not in seen]
        if not nbrs:
            stack.pop()
            continue
        n = rng.choice(nbrs)
        tree.add(tuple(sorted([(c, r), n])))
        seen.add(n)
        stack.append(n)
    edges = [e for e in edges_all if tuple(sorted(e)) in tree or rng.chance(params["loop_chance"])]

    half = cw // 2
    for (c, r), (c2, r2) in edges:
        x0, z0, x1, z1 = room_box(c, r)
        if c2 != c:  # corridor along x
            zc = z0 + 1 + rd // 2
            zl, zh = zc - half, zc - half + cw - 1
            xa, xb = x1, room_box(c2, r2)[0]
            m.fill((xa, 0, zl - 1), (xb, 0, zh + 1), pal.get("corridor", fallback="floor"))
            if cl:
                m.walls((xa, 1, zl - 1), (xb, wh, zh + 1), pal.get("wall"))
            m.fill((xa, 1, zl), (xb, dh, zh), "minecraft:air")
            if params["roof"] and cl:
                m.fill((xa + 1, wh + 1, zl - 1), (xb - 1, wh + 1, zh + 1), pal.get("ceiling"))
        else:  # corridor along z
            xc = x0 + 1 + rw // 2
            xl, xh = xc - half, xc - half + cw - 1
            za, zb = z1, room_box(c2, r2)[1]
            m.fill((xl - 1, 0, za), (xh + 1, 0, zb), pal.get("corridor", fallback="floor"))
            if cl:
                m.walls((xl - 1, 1, za), (xh + 1, wh, zb), pal.get("wall"))
            m.fill((xl, 1, za), (xh, dh, zb), "minecraft:air")
            if params["roof"] and cl:
                m.fill((xl - 1, wh + 1, za + 1), (xh + 1, wh + 1, zb - 1), pal.get("ceiling"))

    # room interiors from the piece library (doorway cells stay clear: pieces keep a 1-cell walkway)
    pieces = [(p, p.get("weight", 1)) for p in params["pieces"]]
    project_dir = getattr(ctx, "project_dir", ".")
    centers = {}
    for r in range(rows):
        for c in range(cols):
            x0, z0, _, _ = room_box(c, r)
            p = rng.weighted(pieces)
            ix, iz = x0 + 1, z0 + 1
            if p["type"] == "builtin":
                centers[(c, r)] = _builtin(p["name"], m, pal, rng, ix, iz, rw, rd, wh)
            else:
                piece = structure_writer.read(os.path.join(project_dir, p["path"]))
                rot = rng.choice([0, 90, 180, 270])
                pm = piece.transformed(rot)
                if pm.size[0] > rw - 2 or pm.size[2] > rd - 2 or pm.size[1] > wh:
                    raise core.MapgenError(f"room_grid: piece {p['path']} ({pm.size}) does not fit a room")
                ox = ix + (rw - pm.size[0]) // 2
                oz = iz + (rd - pm.size[2]) // 2
                m.stamp(pm, (ox, 1, oz))
                centers[(c, r)] = (ix + rw // 2, iz + rd // 2)

    # spawns: one per room at a free cell next to the room centre, spread by the core
    walk = core.Walk(m, ctx.config)
    spawns = []
    for r in range(rows):
        for c in range(cols):
            x0, z0, _, _ = room_box(c, r)
            for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
                cand = (x0 + 1 + rw // 2 + dx, 1, z0 + 1 + rd // 2 + dz)
                if walk.standable(*cand):
                    spawns.append(cand)
                    break
    # extra spawns along room walkways so large player counts fit
    for r in range(rows):
        for c in range(cols):
            x0, z0, _, _ = room_box(c, r)
            for cand in ((x0 + 1, 1, z0 + 1), (x0 + rw, 1, z0 + rd), (x0 + rw, 1, z0 + 1), (x0 + 1, 1, z0 + rd)):
                if walk.standable(*cand) and cand not in spawns:
                    spawns.append(cand)

    markers = []
    if params["objective_rooms"] and spawns:
        reach = walk.reachable_from(spawns[0])
        rooms = sorted(((c, r) for r in range(rows) for c in range(cols)),
                       key=lambda cr: -(abs(cr[0]) + abs(cr[1])))
        for i, (c, r) in enumerate(rooms[:params["objective_rooms"]]):
            x0, z0, _, _ = room_box(c, r)
            ox, oz = x0 + 1 + rw // 2, z0 + 1 + rd // 2
            # objective block goes into the floor at the first free cell near the centre
            for dx, dz in ((0, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                if (ox + dx, 1, oz + dz) in reach:
                    m.set(ox + dx, 0, oz + dz, pal.get("objective"))
                    markers.append({"id": f"goal_{i}", "type": "objective", "pos": [ox + dx, 1, oz + dz]})
                    break

    # connectivity is guaranteed by construction; assert it so a bug can never ship a broken map
    reach = walk.reachable_from(spawns[0])
    lost = [s for s in spawns if s not in reach]
    if lost:
        raise core.MapgenError(f"room_grid: internal error, unreachable spawns {lost[:3]}")
    return {"model": m, "spawns": spawns, "markers": markers,
            "meta": {"rooms": cols * rows, "connections": len(edges), "tree_edges": len(tree)}}
