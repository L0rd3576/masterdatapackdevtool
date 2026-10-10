"""build_budget: placing the map tile by tile stays within config placement limits (blocks per tick, build ticks)."""
NAME = "build_budget"
DESCRIPTION = "Tile placement fits max_blocks_per_tick and max_build_ticks (config placement)."
DEFAULTS = {}


def validate(ctx):
    import structure_writer
    pl = ctx.config["placement"]
    tile = pl["tile_size"]
    vol = tile[0] * tile[1] * tile[2]
    if vol > pl["max_blocks_per_tick"]:
        return [("ERROR", f"tile volume {vol} > max_blocks_per_tick {pl['max_blocks_per_tick']}")]
    per_tick = max(1, pl["max_blocks_per_tick"] // vol)
    n = len(structure_writer.tiles(ctx.result.model.size, tile))
    ticks = -(-n // per_tick)
    msg = f"{n} tile(s) of {tile}, {per_tick} per tick -> {ticks} tick(s)"
    if ticks > pl["max_build_ticks"]:
        return [("ERROR", msg + f" > max_build_ticks {pl['max_build_ticks']}")]
    return [("INFO", msg)]
