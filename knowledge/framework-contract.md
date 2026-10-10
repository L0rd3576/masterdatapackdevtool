# Minigame/map framework contract (tools/build_pack.py + tools/framework/pack)

Everything game-specific is JSON. `build_pack.py <project>` validates it and compiles a datapack. Schemas in `schemas/`
are the source of truth for keys and defaults: read the schema, not this summary, before authoring.
Working example: `examples/slice/` (2 minigames, 3 maps, 1 preset; 6/6 server tests).

## Project layout
```
<project>/project.json        namespace, output, lib_prefix, players {min,max}, arena {dimension, base_y,
                              slot_origin, slot_spacing}, currency {objective, display_name}, end_delay_ticks, gallery, tests
<project>/minigames/<id>.json minigame manifest
<project>/maps/<id>.json      map manifest
<project>/presets/<id>.json   setting/rule overrides of one minigame
<project>/pool.json           enabled minigames (+presets) and maps with weights
<project>/logic/<game>/*.mcfunction   small hook files referenced by the minigame manifest
<project>/structures/*.nbt    hand-made maps (source.structure)
<project>/tests/*.test.json   copied into the built pack
```

## Minigame manifest (`schemas/minigame.schema.json`)
- Required: `id`, `display_name`, `players {min,max}`, `win_condition`, `payout`.
- `map_tags {all_of, any_of, none_of}`: a map qualifies with every all_of tag, at least one any_of tag (if any are
  given), and no none_of tag.
- `rules` (all optional): block_break false, block_place false, pvp true, keep_inventory true, hunger false,
  natural_regeneration true, fall_damage true, time_limit_seconds 180, respawn `eliminate|respawn`, gamemode `auto`
  (auto = survival if breaking/placing is allowed, else adventure), clear_inventory true, effects [].
  Applied through `mcdp_lib:rules/apply` and reverted at teardown.
- `settings`: name -> {type, default, min, max, description}. The values reach logic as `storage <ns>:round settings.<name>`.
- `win_condition`: a folder `tools/framework/pack/data/__ns__/function/win/<id>/` (`last_standing`,
  `highest_score`, `survive`). Add a win condition by adding a folder with `check` + `winners`.
- `payout {type: linear|pot, base, per_participant, participation}`, with n = participants at round start.
  linear: each winner gets base + per_participant*n. pot: that sum split evenly (floor). Everyone also gets participation.
- `functions`: hook files `load`, `start`, `player_start`, `tick`, `eliminated`, `end` (missing = no-op).

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
  apply rules, teleport to spawns, hooks -> `round/tick` (win check, timer) -> `round/end` -> payout ->
  revert rules -> `_restore` (re-place tiles if `needs_restore`) -> idle. State: score `#state <ns>.round`.

## Checks
`python tools/mapgen/validate.py <project> [--maps]`: schemas (unknown key = WARN, missing/bad = ERROR with file
+ JSON path), cross-references. ERROR: id differs from the file name, duplicate id, min > max, unknown
win_condition / minigame / preset / map, missing hook file, a preset setting with the wrong type or out of range,
a pooled game with no compatible enabled map. WARN: unused map, player counts with no combination, block rules
that the gamemode cannot enforce (survival cannot stop placing). Then run `build_pack.py`, `lint_datapack.py`,
`run_tests.py`.
