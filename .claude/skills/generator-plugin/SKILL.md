---
name: generator-plugin
description: Use when adding or changing a map generator or map validator plugin in tools/mapgen (procedural arenas, rooms, terrain, new validation checks), or when a map fails the determinism validator.
---

# Generator and validator plugins (tools/mapgen)

Adding a plugin = adding one file. Core code never changes. Discovery: `tools/mapgen/registry.py` loads every
`*.py` (not starting with `_`) in `config.json plugin_dirs.generators|validators` plus any `--plugin-dir`.
A missing attribute or a duplicate NAME is a hard error. Examples: `generators/static_arena.py` (simple),
`room_grid.py` (piece library + guaranteed connectivity), `heightmap_terrain.py` (noise).

## Generator file `tools/mapgen/generators/<name>.py`
```python
NAME = "my_gen"                      # value of source.generator in map manifests
DESCRIPTION = "one line"
PARAMS_SCHEMA = {"type": "object", "properties": {
    "size": {"type": "array", "items": {"type": "integer", "minimum": 7}, "minItems": 3, "maxItems": 3,
             "default": [25, 8, 25], "description": "..."},
    "palette": {"$ref": "common.schema.json#/definitions/palette_ref"}},
    "additionalProperties": False}  # every param has a default + description; manifests are checked against it

def generate(params, rng, ctx):      # params: defaults merged in; rng: seeded (rng.py); ctx: core.GenContext
    from model import Model
    import core
    m = Model(tuple(params["size"]))
    m.fill((0, 0, 0), (params["size"][0] - 1, 0, params["size"][2] - 1), ctx.palette.get("floor", rng))
    return {"model": m, "spawns": [[x, 1, z], ...], "markers": [{"id": "center", "type": "objective", "pos": [x, 1, z]}],
            "meta": {...}}           # spawns = feet cells (floor y + 1), local coordinates
```
- `ctx`: `config`, `manifest`, `palette` (`.get(role, rng=None, fallback=None)`; roles come from config
  palettes), `max_players`, `project_dir`. Raise `core.MapgenError("...")` for bad param combinations.
- Model ops: `set/get/clear/fill/hollow/walls/line/column/heightmap/stamp(other, origin, rotation, mirror)/
  transformed/top_y/set_block_entity/add_entity`. Noise: `noise.py` (seeded). Walkability: `core.Walk(m, config)`
  `.reachable_from(cell)`. Use it to keep connectivity, as static_arena does with obstacles.
- No hard-coded blocks or numbers: put them in params (with defaults) or palette roles in config.

## Determinism rules (the `determinism` validator enforces them)
- Draw randomness only from `rng` (`random()`, `randint`, `chance`, `choice`, `weighted`). Never use the
  `random` module, `time`, `uuid`, `hash()`, or iteration over a `set`/`dict` built from unordered input.
  Sort before choosing.
- Proven by `tools/mapgen/selftest/plugins/selftest_nondeterministic.py`, which must fail.

## Validator file `tools/mapgen/validators/<name>.py`
```python
NAME = "my_check"; DESCRIPTION = "one line"; DEFAULTS = {"threshold": 3}   # override in config validators.settings.<name>
def validate(ctx):   # ctx.result (manifest, model, spawns, markers, seed, params, meta), ctx.config, ctx.settings
    return [("ERROR", "msg")]   # or ("WARN"/"INFO", ...); [] = pass
```
Set `NEEDS_SERVER = True` for checks that use `ctx.server`; offline runs then SKIP them (see `server_load.py`).
Enable it by adding NAME to `config.json validators.enabled`. Per map: manifest `validation: {name: false}`
skips it, and `{name: {...}}` overrides its thresholds.

## Verify (all must pass)
1. `python tools/mapgen/validate.py --config`
2. A map manifest that uses the generator: `python tools/mapgen/report.py <manifest>` (includes server load).
   Read the top-down PNG.
3. `python tools/mapgen/selftest_failures.py` (the broken fixtures are still caught) and `python tools/selftest.py --fast`.
