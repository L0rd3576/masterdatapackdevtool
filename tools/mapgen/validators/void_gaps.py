"""void_gaps: from any reachable cell, no step leads into a column with nothing standable below (a hole into the
void) or off the model edge (into the untouched arena void). Counts distinct gap columns; threshold max_gaps."""
NAME = "void_gaps"
DESCRIPTION = "No accidental holes/edges where a player can fall into the void."
DEFAULTS = {"max_gaps": 0}


def validate(ctx):
    import core
    m = ctx.result.model
    if not ctx.result.spawns:
        return []
    walk = core.Walk(m, ctx.config)
    reach = set()
    for s in ctx.result.spawns:
        if tuple(s) not in reach:
            reach |= walk.reachable_from(tuple(s))
    gaps = set()
    for (x, y, z) in reach:
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            if not (0 <= nx < m.size[0] and 0 <= nz < m.size[2]):
                gaps.add((nx, nz))  # nothing stops the player walking off the model
                continue
            if not all(walk.free(nx, y + h, nz) for h in range(walk.headroom)):
                continue  # wall: cannot step there
            if not any(walk.bc.classify(m.get(nx, yy, nz))[1] for yy in range(y - 1, -1, -1)):
                gaps.add((nx, nz))
    if len(gaps) > ctx.settings["max_gaps"]:
        sample = ", ".join(str(list(g)) for g in sorted(gaps)[:6])
        return [("ERROR", f"{len(gaps)} void gap column(s) (max {ctx.settings['max_gaps']}): {sample}")]
    return [("INFO", f"{len(gaps)} void gap column(s) (allowed {ctx.settings['max_gaps']})")] if gaps else []
