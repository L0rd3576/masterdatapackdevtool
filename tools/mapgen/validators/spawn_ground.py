"""spawn_ground: each spawn cell has a standable solid block below and config movement.headroom free cells."""
NAME = "spawn_ground"
DESCRIPTION = "Spawns stand on solid ground with headroom (config movement.headroom)."
DEFAULTS = {}


def validate(ctx):
    import core
    m = ctx.result.model
    walk = core.Walk(m, ctx.config)
    out = []
    for i, (x, y, z) in enumerate(ctx.result.spawns):
        if not walk.standable(x, y, z):
            below = m.get(x, y - 1, z)
            body = [m.get(x, y + h, z) or "air" for h in range(walk.headroom)]
            out.append(("ERROR", f"spawn #{i} {[x, y, z]} is not standable: below={below or 'nothing'}, body={body}"))
    return out
