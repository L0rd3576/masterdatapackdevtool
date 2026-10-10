"""spawn_count: at least players.max distinct spawn points (one per participant)."""
NAME = "spawn_count"
DESCRIPTION = "Enough spawn points for the map's max players (+ optional spare)."
DEFAULTS = {"spare": 0}


def validate(ctx):
    mx = ctx.result.manifest["players"]["max"]
    need = mx + ctx.settings["spare"]
    have = len(ctx.result.spawns)
    out = []
    if have < need:
        out.append(("ERROR", f"{have} spawn point(s) for max {mx} players (+{ctx.settings['spare']} spare): need {need}"))
    dup = have - len(set(map(tuple, ctx.result.spawns)))
    if dup:
        out.append(("ERROR", f"{dup} duplicate spawn point(s)"))
    return out
