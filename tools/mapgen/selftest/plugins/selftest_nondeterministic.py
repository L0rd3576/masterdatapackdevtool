"""selftest_nondeterministic: DELIBERATELY BROKEN generator for tools/mapgen/selftest_failures.py.
It draws from the global `random` module instead of the seeded rng, so the determinism validator must fail it.
Everything else is valid (walled floor), so determinism is the only validator that fails.
Never add this dir to config plugin_dirs."""
import random

NAME = "selftest_nondeterministic"
DESCRIPTION = "Broken on purpose: walled floor with one pillar placed by unseeded global random."
PARAMS_SCHEMA = {"type": "object", "properties": {}, "additionalProperties": False}


def generate(params, rng, ctx):
    from model import Model
    m = Model((9, 4, 9))
    floor, wall = ctx.palette.get("floor"), ctx.palette.get("wall")
    m.fill((0, 0, 0), (8, 0, 8), floor)
    for x, z in ((0, None), (8, None), (None, 0), (None, 8)):
        m.fill((x if x is not None else 0, 1, z if z is not None else 0),
               (x if x is not None else 8, 3, z if z is not None else 8), wall)
    m.set(random.randint(3, 5), 1, random.randint(3, 5), wall)  # the bug: global random ignores the seed
    return {"model": m, "spawns": [[1, 1, 1], [7, 1, 7]], "markers": []}
