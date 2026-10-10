---
name: minigame-manifest
description: Use when adding or changing a minigame, preset, or pool entry in a Minecraft 26.3 framework project (minigames/<id>.json, presets/, pool.json, logic/ hook functions, win conditions, payouts, rules), or when building/testing a framework pack with tools/build_pack.py.
---

# Minigame manifests and the framework build (Minecraft Java 26.3)

Workspace `C:\Users\lrafy\mc-datapack-tools`. Contract and defaults: `knowledge/framework-contract.md`.
Schemas: `schemas/minigame.schema.json`, `preset.schema.json`, `pool.schema.json`, `project.schema.json`.
Example: `examples/slice/` (`pvp_arena` = no block breaking, last standing; `block_brawl` = breakable map,
highest score, restored after the round).

## Procedure
1. **Manifest** `minigames/<id>.json`. Required: id (= file name), display_name, players {min,max},
   win_condition, payout. Leave out any rule that should keep its default (see the schema `default`s).
   - `map_tags`: use `any_of` for "needs one of these features" and `none_of` to exclude maps.
   - Each `settings` entry needs {type, default, min/max or options, description}. Logic reads
     `storage <ns>:round settings.<name>`.
   - `win_condition`: one of the folders in `tools/framework/pack/data/__ns__/function/win/`.
   - `payout`: `linear` (each winner base + per_participant*n) or `pot` (split), plus `participation`.
2. **Hooks** go in `logic/<id>/*.mcfunction`, referenced from `functions` (load, start, player_start, tick,
   eliminated, end). Keep them small. Write `__ns__` for the project namespace and `__lib__` for the vendored
   library: build_pack substitutes both and copies hooks to `function/game/<id>/<hook>.mcfunction` (missing hooks
   become stubs). Framework tags you can use: `__ns__.in_round`, `__ns__.alive`; score `__ns__.score`.
   Call mcdp_lib before writing helpers (`library/INDEX.md`).
   Look up every command with `tools/cmd_syntax.py`.
3. **Preset** (optional) `presets/<id>.json`: {id, minigame, display_name, settings?, rules?}.
4. **Pool**: add `{id, weight, presets: [{id, weight}]}` to `pool.json` minigames.
5. **Check**: `python tools/mapgen/validate.py <project> --maps`. Fix every ERROR, and read the WARNs: "no
   combination for player counts" means some player count in the project range has no game+map.
6. **Build**: `python tools/build_pack.py <project>`, then `python tools/lint_datapack.py <out>`.
7. **Test**: add `<project>/tests/<x>.test.json` (format: `knowledge/testing.md`). There are no fake players in
   26.3 vanilla. Summon armor stands tagged `t.p` and run `execute as @e[tag=t.p] run function <ns>:queue/join`
   (see `examples/slice/tests/_make_tests.py`). Then `python tools/run_tests.py <out>` must PASS.

## Adding a win condition or payout type
- A win condition is a new folder `win/<id>/` with `check.mcfunction` (end the round when decided) and
  `winners.mcfunction` (tag the winners). Copy `win/last_standing`. No core edits: `project.py` discovers folders.
- A payout type needs a `build_pack.py` change plus a schema enum entry. Prefer expressing a new formula with
  base/per_participant/participation first.

## Pitfalls
- `assert` steps in tests are `execute <condition>`: start them with `if`/`unless`/`in`, never `entity ...`
  (seen twice: `execute entity ...` is a parse error).
- `block_place:false` cannot be enforced in survival (WARN). Use gamemode auto/adventure when nothing is breakable.
- Rules are reverted at teardown through mcdp_lib. Never set gamerules directly in hooks.
