"""spawn_reachability: every spawn can walk to every other spawn (flood fill over walkable cells; moves use config
movement: jump_up, max_drop, headroom, jump_headroom). Drops are one-way, so mutual mode also checks the way back."""
NAME = "spawn_reachability"
DESCRIPTION = "All spawns mutually reachable on foot (flood fill with config movement values)."
DEFAULTS = {"mode": "mutual"}


def validate(ctx):
    import core
    sp = [tuple(s) for s in ctx.result.spawns]
    if len(sp) < 2:
        return []
    walk = core.Walk(ctx.result.model, ctx.config)
    out = []
    reach = walk.reachable_from(sp[0])
    lost = [i for i, s in enumerate(sp) if s not in reach]
    if lost:
        out.append(("ERROR", f"{len(lost)} spawn(s) unreachable from spawn #0 {list(sp[0])}: "
                             + ", ".join(f"#{i} {list(sp[i])}" for i in lost[:6])))
    if ctx.settings["mode"] == "mutual":
        for i, s in enumerate(sp[1:], 1):
            if i not in lost and sp[0] not in walk.reachable_from(s):
                out.append(("ERROR", f"spawn #{i} {list(s)} cannot walk back to spawn #0 (one-way drop)"))
    return out
