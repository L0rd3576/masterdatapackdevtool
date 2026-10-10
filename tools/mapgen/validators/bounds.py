"""bounds: the model matches the manifest size (if given), fits config limits and the world height at the
target y, and every spawn/marker lies inside the model."""
NAME = "bounds"
DESCRIPTION = "Size matches manifest/config limits; spawns and markers inside the model; fits world height."
DEFAULTS = {"base_y": 64}


def validate(ctx):
    import constants
    out = []
    m, man = ctx.result.model, ctx.result.manifest
    if man.get("size") and list(man["size"]) != list(m.size):
        out.append(("ERROR", f"model size {list(m.size)} != manifest size {man['size']}"))
    lim = ctx.config["limits"]
    if any(s > x for s, x in zip(m.size, lim["max_size"])):
        out.append(("ERROR", f"size {list(m.size)} exceeds limits.max_size {lim['max_size']}"))
    base_y = ctx.settings["base_y"]
    top = base_y + m.size[1]
    world_top = constants.OVERWORLD_MIN_Y + constants.OVERWORLD_HEIGHT
    if base_y < constants.OVERWORLD_MIN_Y or top > world_top:
        out.append(("ERROR", f"placed at y={base_y} the map spans y {base_y}..{top - 1}, outside the world "
                             f"({constants.OVERWORLD_MIN_Y}..{world_top - 1})"))
    for i, s in enumerate(ctx.result.spawns):
        if not m.inside(*s):
            out.append(("ERROR", f"spawn #{i} {list(s)} is outside the model {list(m.size)}"))
    for mk in ctx.result.markers:
        if not m.inside(*mk["pos"]):
            out.append(("ERROR", f"marker {mk['id']} {mk['pos']} is outside the model {list(m.size)}"))
    return out
