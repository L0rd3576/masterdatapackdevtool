# Map generation (tools/mapgen) - verified facts and how the tools fit

[V] = verified in this workspace (file, probe, or passing test). [W] = Minecraft Wiki only.

## Structure .nbt format (26.3)
- [V] All 1511 vanilla structures in `reference/vanilla-data/minecraft/structure/` have `DataVersion 5023`; root keys
  `size`, `palette` (or `palettes`), `blocks`, `entities`, `DataVersion`. Palette entries are `{id, properties}`
  (not the old `Name`/`Properties`). Blocks `{pos, state, nbt?}`; entities `{pos (double), blockPos (int), nbt}`.
  Constants live in `tools/mapgen/constants.py`.
- [V] Round trip: `report.py` writes the file, places it on the 26.3 test server with `place template`, and reads
  `server_check.sample_blocks` positions back (`server_load: ... 72 sampled blocks match`, 2026-10-10).
- `structure.fill_air` (config) writes air into every untouched cell, so re-placing a template clears the volume.
  The framework's map restore depends on this.

## Size limits and placement
- [V] Probe 2026-10-10: `place template` loaded and placed 200x1x200, 64x4x64 and 48x192x8 stone templates
  (`Loaded template "pb:flat200" at 0, 0, 0`, 341 ms, corner block read back). `place template` has no 48-block limit.
- [W] The structure block UI can only save 48x48x48. That limit does not apply to files we write ourselves.
- `limits.max_size` / `max_volume` in config are tool limits (memory, build time), not game limits. World height
  comes from `dimension_type` (`constants.OVERWORLD_MIN_Y/HEIGHT`).
- The target area must be loaded. The framework `forceload add`s each map slot before placing it.
- Large maps are cut into `placement.tile_size` tiles (default 16^3). `place/tick` places `tiles_per_tick` of them
  per tick (derived from `max_blocks_per_tick`, ~8192 blocks, about one 50 ms tick at ~160 blocks/ms measured).
  The `build_budget` validator fails a map needing more than `max_build_ticks`.
- [V] Summoning entities (text_display labels) in the same function as `forceload add` of a fresh chunk lost
  3-6 of 9 entities under `run_tests` (entity sections not loaded yet). The gallery therefore forceloads first and
  places after `gallery.place_delay_ticks` (20). Do the same for any marker or entity you summon into a newly
  forceloaded area.

## Arena dimension
- [V] `data/<ns>/dimension/<name>.json` = `{type: "minecraft:overworld", generator: {type: "minecraft:flat",
  settings: {biome: "minecraft:the_void", features: false, lakes: false, layers: []}}}`. The generator shape is copied
  from `reference/vanilla-data/minecraft/worldgen/world_preset/flat.json`. It loads on 26.3, and slice tests place
  into it with `execute in slice:arena`.
- Each map gets a slot `project.arena.slot_spacing` apart. The gallery row is at config `gallery.origin` (z=4096).

## Movement values used by reachability (config `movement`, cells)
- [V] Probe: zombie attribute base values `step_height 0.6`, `jump_strength 0.41999998688697815`, `gravity 0.08`,
  `safe_fall_distance 3.0`. Players share these LivingEntity defaults [W].
- So: a 1-block rise needs a jump (0.6 < 1). The jump apex is ~1.25 blocks (`constants.jump_apex()`), so `jump_up 1`.
  `max_drop 3` = safe fall. `headroom 2` (player 1.8 tall [W]). `jump_headroom 3`.

## Determinism
- Generators get a seeded `rng` (`tools/mapgen/rng.py`, splitmix64). They must never use `random`, `time`,
  `hash()` or set iteration order. The `determinism` validator regenerates in-process (global `random` reseeded
  in between) and in a subprocess with another PYTHONHASHSEED, and compares sha256.
- A seed comes from `source.seed`, or is derived from `sha256(config.seed.salt + map id)`.

## Players in tests
- [V] 26.3 has no vanilla fake-player command (`commands.json` root has no `player`; that is the Carpet mod).
  GameTest mock players are Java-only. The slice tests use armor stands tagged `t.p` as stand-ins
  (`queue/join` as them). They cover selection, teleport, rules, payout and restore. Not covered: real player
  input, death and respawn screens, gamemode on players, inventory (see `UNVERIFIED.md`).

## Tools (all `python tools/mapgen/<x>.py`)
`generate.py` (.nbt + meta, `--hash`), `render.py` (top/layers PNG + ASCII), `validate.py` (schemas, cross-refs,
`--maps`), `report.py` (everything + server load), `gallery.py` (`--check`), `selftest_failures.py` (3 broken
fixtures must fail). Plugins: `generators/`, `validators/` (see skill `generator-plugin`).
