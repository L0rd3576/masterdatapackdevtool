# Minigame/map framework contract (tools/build_pack.py + tools/framework/pack)

Everything game-specific is JSON. `build_pack.py <project>` validates it and compiles a datapack. Schemas in `schemas/`
are the source of truth for keys and defaults: read the schema, not this summary, before authoring.
Working example: `examples/slice/` (3 minigames, 3 maps, 1 preset; 10/10 server tests).

## Project layout
```
<project>/project.json        namespace, output, output_mode, lib_prefix, players {min,max}, arena {dimension, base_y,
                              slot_origin, slot_spacing}, currency {objective, display_name}, end_delay_ticks, gallery,
                              tests, pack_src, functions {load, tick}
<project>/<pack_src>/data/... hand-written pack files copied over the build (overlay)
<project>/minigames/<id>.json minigame manifest
<project>/maps/<id>.json      map manifest
<project>/presets/<id>.json   setting/rule overrides of one minigame
<project>/pool.json           enabled minigames (+presets) and maps with weights
<project>/logic/<game>/*.mcfunction   small hook files referenced by the minigame manifest
<project>/structures/*.nbt    hand-made maps (source.structure)
<project>/tests/*.test.json   copied into the built pack
```

## Project options for bigger packs (`schemas/project.schema.json`; slice + `tools/selftest.py` prove them)
- `output_mode`: `replace` (default) deletes and rewrites the whole output dir, only if build_pack made it
  (`.built_by_build_pack`); a project inside the output is refused. `merge` deletes and rewrites only `data/`,
  `tests/`, `pack.mcmeta`, `.build_pack_owned`; every other file stays (docs, `src/` itself, e.g. `output: ".."`).
  An output with `data/` but no `.build_pack_owned` is refused unless `build_pack.py --adopt` (takes it over once).
  ERROR if the project, its tests or pack_src dir lies inside `out/data` or `out/tests`.
- `pack_src`: dir copied into the output after everything else; `__ns__`/`__lib__` replaced in paths and in
  `.mcfunction`/`.json` text; other files copied as bytes. A file the build already wrote is a build ERROR naming
  both paths (never override framework files; hook into them via `functions` and minigame hooks instead).
- `functions {load: [ids], tick: [ids]}` (default empty): compiled into `data/<ns>/tags/function/extra_load.json`,
  `extra_tick.json`. `<ns>:load` runs `#<ns>:extra_load` last (after minigame load hooks); `<ns>:tick` runs
  `#<ns>:extra_tick` first, every tick in every state. The build fails if a listed function is not in the pack.
  Do not add your own `#minecraft:load/tick` entries in pack_src (collision ERROR); use these lists.

## Minigame manifest (`schemas/minigame.schema.json`)
- Required: `id`, `display_name`, `players {min,max}`, `win_condition`, `payout`.
- `map_tags {all_of, any_of, none_of}`: a map qualifies with every all_of tag, at least one any_of tag (if any are
  given), and no none_of tag.
- `rules` (all optional): block_break false, block_place false, pvp true, keep_inventory true, hunger false,
  natural_regeneration true, fall_damage true, time_limit_seconds 180, time_up `end|hook` (end), respawn
  `eliminate|respawn`, gamemode `auto` (auto = survival if breaking/placing is allowed, else adventure),
  clear_inventory true, effects []. Applied through `mcdp_lib:rules/apply` and reverted at teardown (time_up is
  framework-only: it is read from `storage <ns>:round current.rules`, not passed to the library).
- `settings`: name -> {type, default, min, max, description}. The values reach logic as `storage <ns>:round settings.<name>`.
- `win_condition`: a folder `tools/framework/pack/data/__ns__/function/win/<id>/` (`last_standing`, `last_team`,
  `highest_score`, `survive`). Add a win condition by adding a folder with `check` + `winners`.
  `last_team`: ends when at most one distinct `<ns>.tid` is alive. `round/start_with` gives every participant a
  unique tid 1..n (free-for-all); team games overwrite `<ns>.tid` in their `start` hook (same tid = same team).
  Winners: every participant (also eliminated ones) whose team has someone alive; nobody alive -> the teams of
  everyone tagged `<ns>.elim_now` win (same-tick tie; `round/eliminate` adds it, `round/tick` clears it as its first
  line, so only eliminations inside round/tick (tick hook, deaths) count as "this tick"). Time-up end: all alive teams.
- `payout {type: linear|pot, base, per_participant, participation}`, with n = participants at round start.
  linear: each winner gets base + per_participant*n. pot: that sum split evenly (floor). Everyone also gets participation.
  Both amounts are multiplied by `#mult_pct <ns>.round` / 100 before the pot split (start_with sets 100; a game's
  `start` hook may change it, e.g. 150 = 1.5x). `storage <ns>:round last_payout {winner, participation}` = scaled values.
- `functions`: hook files (missing = no-op): `load`, `start`, `player_start`, `tick`, `eliminated`, `time_up`
  (time limit reached and rules.time_up "hook": runs once, round keeps running), `end` (before payout), `results`
  (after payout and the winner message), `teardown` (once, after rules revert and restore_*, in_round tags still set;
  also runs on `round/abort` after the map was placed).

## Map manifest (`schemas/map.schema.json`)
- Required: `id`, `display_name`, `tags`, `players`, `source`.
- `source`: `{"structure": "structures/x.nbt"}` or `{"generator": name, "params": {...}, "seed"?: int}`.
- `spawns` (local cells) override generator spawns (or use `spawn_rules`). `markers` are objective points.
  `needs_restore` makes the map re-placed after the round. `tag_meta` is free per-tag data. `validation`
  overrides validator settings for this map.

## Preset / pool
- Preset: `id`, `minigame`, `display_name`, `settings` and/or `rules` overrides (checked against the game's specs).
- Pool: `minigames: [{id, weight, presets: [{id, weight}]}]`, `maps: [{id, weight}]`. Only pooled entries are built.

## What the build emits
- `storage <ns>:registry` `games`, `maps`, `by_count.n<N>` (weighted list of compatible game+preset+map for N
  players, computed at build time from player ranges and tags).
- Map tiles `data/<ns>/structure/map/<id>/t<i>.nbt`, the arena dimension, gallery functions, and vendored mcdp_lib.
- Round flow (`<ns>:round/*`): `queue/join` -> `round/start` (count queued, `_pick` weighted via
  `mcdp_lib:random/weighted`, or `_no_candidates` sets `round.last_error`) -> place tiles over ticks (`place/*`) ->
  apply rules, teleport to spawns, hooks -> `round/tick` (win check, timer; `round/time_up` ends or runs the
  time_up hook) -> `round/end` (end hook) -> payout -> results hook -> revert rules, restore participants ->
  teardown hook -> `_restore` (re-place tiles if `needs_restore`) -> idle. State: score `#state <ns>.round`.
  Every tick `<ns>:tick` first runs `#<ns>:extra_tick` (project functions).

## Checks
`python tools/mapgen/validate.py <project> [--maps]`: schemas (unknown key = WARN, missing/bad = ERROR with file
+ JSON path), cross-references. ERROR: id differs from the file name, duplicate id, min > max, unknown
win_condition / minigame / preset / map, missing hook file, a preset setting with the wrong type or out of range,
a pooled game with no compatible enabled map. WARN: unused map, player counts with no combination, block rules
that the gamemode cannot enforce (survival cannot stop placing), rules.time_up "hook" without a time_up hook.
Pool weight 0 = built into the registry (startable with `round/start_with`) but never picked by `round/start`. Then run `build_pack.py`, `lint_datapack.py`,
`run_tests.py`.
