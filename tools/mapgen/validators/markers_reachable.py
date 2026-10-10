"""markers_reachable: every marker with reachable=true has a reachable walkable cell within `near` cells of it
(horizontally, +-1 in y), starting from spawn #0."""
NAME = "markers_reachable"
DESCRIPTION = "Objective markers reachable on foot from the spawns."
DEFAULTS = {"near": 1}


def validate(ctx):
    import core
    if not ctx.result.spawns:
        return []
    walk = core.Walk(ctx.result.model, ctx.config)
    reach = walk.reachable_from(tuple(ctx.result.spawns[0]))
    n = ctx.settings["near"]
    out = []
    for mk in ctx.result.markers:
        if not mk.get("reachable", True):
            continue
        x, y, z = mk["pos"]
        if not any((x + dx, y + dy, z + dz) in reach
                   for dx in range(-n, n + 1) for dz in range(-n, n + 1) for dy in (-1, 0, 1)):
            out.append(("ERROR", f"marker {mk['id']} {mk['pos']} is not reachable from spawn #0"))
    return out
