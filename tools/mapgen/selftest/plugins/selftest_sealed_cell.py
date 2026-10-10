"""selftest_sealed_cell: DELIBERATELY BROKEN map for tools/mapgen/selftest_failures.py.
A walled 11x11 floor with a sealed 3x3 cell in the middle (walls 3 high, above jump height). Spawn #1 is inside
the cell, so spawn_reachability must fail; every other validator passes. Never add this dir to config plugin_dirs."""
NAME = "selftest_sealed_cell"
DESCRIPTION = "Broken on purpose: one spawn sealed inside a walled cell."
PARAMS_SCHEMA = {"type": "object", "properties": {}, "additionalProperties": False}


def _ring(m, lo, hi, top, state):
    for y in range(1, top + 1):
        for i in range(lo, hi + 1):
            for x, z in ((i, lo), (i, hi), (lo, i), (hi, i)):
                m.set(x, y, z, state)


def generate(params, rng, ctx):
    from model import Model
    m = Model((11, 5, 11))
    floor, wall = ctx.palette.get("floor"), ctx.palette.get("wall")
    m.fill((0, 0, 0), (10, 0, 10), floor)
    _ring(m, 0, 10, 4, wall)  # outer wall
    _ring(m, 3, 7, 3, wall)   # sealed cell around (5, 5)
    return {"model": m, "spawns": [[1, 1, 1], [5, 1, 5]], "markers": []}
