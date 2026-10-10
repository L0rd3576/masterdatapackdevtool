"""spawn_hazard: no hazard block (config blocks.hazard) in or next to a spawn: `radius` cells around it, from the
block below the feet to the top of the headroom."""
NAME = "spawn_hazard"
DESCRIPTION = "No hazard blocks (lava, fire, cactus, ...) within `radius` of any spawn."
DEFAULTS = {"radius": 1}


def validate(ctx):
    import core
    bc = core.BlockClasses(ctx.config)
    m = ctx.result.model
    r = ctx.settings["radius"]
    head = ctx.config["movement"]["headroom"]
    out = []
    for i, (x, y, z) in enumerate(ctx.result.spawns):
        hits = []
        for dy in range(-1, head):
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    st = m.get(x + dx, y + dy, z + dz)
                    if st is not None and bc.classify(st)[2]:
                        hits.append(f"{st.split('[')[0]}@{[x + dx, y + dy, z + dz]}")
        if hits:
            out.append(("ERROR", f"spawn #{i} {[x, y, z]} is next to hazard(s): {', '.join(hits[:4])}"))
    return out
