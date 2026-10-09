# Prompt 2 for Claude Code: map generator + minigame/map data contract (Minecraft 26.3)

Run from `C:\Users\lrafy\mc-datapack-tools` AFTER prompt 1 has finished (linter, test runner, generated reports, and knowledge/ must exist). Suggested launch: `claude --model opus --effort high`, plan mode first.

---

You are adding procedural map generation and a data-driven minigame/map framework contract to the datapack master workspace. Read `CLAUDE.md` first and obey it (verify syntax from `generated/` and `knowledge/`, lint after edits, run server tests, log lessons, create skills for repeated patterns).

## Design principle: flexible, data-driven, almost no hard-coded values
- Nothing game-specific lives in code. Block palettes, sizes, tag names, player ranges, rule names, payout formulas, generator parameters, validator thresholds, tick budgets, and namespaces all come from JSON config or manifest files with documented defaults.
- Every JSON file type has a schema file in `schemas/` (JSON Schema draft-07 style, validated by a small stdlib validator you write, or by `jsonschema` only if the user approves installing it). Unknown keys produce warnings; missing required keys produce errors with the file path and key.
- Generators, validators, and renderers are plugins: a registry maps a name in the manifest (`"generator": "room_grid"`) to a Python module in `tools/mapgen/generators/`. Adding one means adding a file, never editing core code.
- Use `tools/mapgen/config.json` for tool-level settings (output dirs, default palette, seed handling, size limits taken from verified 26.3 data). When you need a number, ask "is this a config value?" first. Constants that are truly fixed by the game (verified from the jar) go in one `constants` module with a source comment.
- Python 3 stdlib only unless the user approves a package. Everything must run on Windows, called as `python tools/mapgen/<tool>.py`.

## Data contract (JSON, with schemas in `schemas/`)
1. **Minigame manifest** (`minigames/<id>.json`): id, display name, min/max players, required map tags (with any-of/all-of/none-of), rules (block_break, block_place, pvp, keep_inventory, hunger, time_limit_seconds, respawn, gamemode, etc., all optional with defaults), tweakable `settings` (each with type, default, min, max, description), win condition id, and a `payout` block (formula type plus parameters, e.g. base amount scaled by participant count).
2. **Map manifest** (`maps/<id>.json`): id, tags, supported player range, bounds/size, spawn points (or rules to derive them), objective markers, source (`"structure": path` or `"generator": name` plus `params` and optional fixed `seed`), needs_restore flag, and per-tag metadata.
3. **Presets** (`presets/<id>.json`): named overrides of minigame settings.
4. **Pool config** (`pool.json`): enabled minigames/maps and selection weights.
All of these are authored by hand or by Claude. A build tool, `tools/build_pack.py`, validates them and compiles them into a datapack: runtime data in `data storage`, selector functions, round setup and teardown functions, rule application, restore logic, payout functions. The generated datapack contains no hand-written minigame logic outside the framework; minigame-specific logic comes from small function files referenced by the manifest.

## Map generation tools (`tools/mapgen/`)
- `nbt.py` / `structure_writer.py`: write valid 26.3 structure `.nbt` files (verify the exact format from vanilla structures in `reference/vanilla-data/` and a round-trip test: write, load on the test server with `place template`, read blocks back).
- Block-grid model in memory: sparse blocks with palette indices, block states, optional block entities, entities. Operations: fill, box, hollow, line, noise heightmap, stamp another model with rotation/mirror.
- Generators (each takes `params`, `seed`, `config`, returns a model plus metadata for spawns/markers):
  - `static_arena`: small fixed arena from parameters (size, floor/wall palette, obstacles density).
  - `room_grid`: grid of rooms/corridors from a piece library, with connectivity guaranteed.
  - `heightmap_terrain`: noise-based natural terrain (implemented from scratch with seeded value or simplex noise); scaffolding for later large landscapes. Check structure size limits and placement approaches in 26.3 and document the findings in `knowledge/mapgen.md`.
- Same seed + same params must produce byte-identical output (test this).
- Placement: use `place template` or other verified commands; chunk large placements across ticks with a configurable tick budget; keep arenas in a dedicated datapack-defined void dimension (verify dimension JSON format for 26.3) separate from the player world.

## Validators (`tools/mapgen/validators/`, pluggable, thresholds from config)
bounds respected; enough spawn points for max players; spawns on solid ground with headroom; no spawn in hazards; all spawns mutually reachable (flood fill over walkable cells using config-defined step height/jump height; verify game movement values from reliable sources and cite them); objective markers reachable; no accidental void gaps; seed determinism; structure loads on the real server without errors; build time within tick budget.

## Inspection tools
- `tools/mapgen/render.py`: top-down and per-layer PNG renders from a model using a config color map (write PNGs with stdlib `zlib`/`struct`), plus ASCII layer dumps. Claude must look at renders (view the image) when reviewing maps.
- `tools/mapgen/gallery.py`: builds a catalog area in the arena dimension where every map in the pool is placed side by side with signs/labels so the user can walk through them in-game.
- `tools/mapgen/report.py`: one command that generates a map from a manifest, runs all validators, renders it, loads it on the test server, and prints a pass/fail report with paths to renders.

## Autonomy loop for new maps
Document in `.claude/skills/map-authoring/SKILL.md` the loop: write the manifest, generate, validate, render and review the image, test on the server, fix, repeat until clean, add to pool, update the gallery. Include a "style notes" file `knowledge/map-style.md` that records the user's approved aesthetic and constraints from reviewed examples so future maps need little direction.

## Vertical slice (prove the contract before widening)
Build in `examples/slice/`:
- 2 simple minigames (e.g. a small PvP arena where blocks cannot be broken, and a minigame where blocks can be broken and must be restored after the round). Keep game logic minimal; the point is the framework.
- 3 maps: one only for the PvP game, one shared by both via tags, one generated by `room_grid`.
- Selector picks a random compatible minigame/map for the current player count (3-10 players), applies rules, runs the round, awards currency by participant count, tears down, restores the map.
- Tests on the real server using fake players if available in 26.3 (research how; if not available, simulate with armor stands/markers and scoreboard-driven stand-ins and document the limitation honestly).
- Lint and test pass on the final pack. Include 3 self-tests that must fail: a manifest with a missing required key, an unreachable spawn, a non-deterministic generator.

## Documentation and self-improvement
Add `knowledge/mapgen.md` and `knowledge/framework-contract.md`, extend `CLAUDE.md` index (keep it under 200 lines), log mistakes to `knowledge/lessons.md`, and create skills for repeated patterns (`map-authoring`, `minigame-manifest`, `generator-plugin`).

## Definition of done
Do not stop at writing files. Show real output for: schema validation failing on a bad manifest, a generated map with passing validators and a render you reviewed, the slice pack passing lint and the server test run, the three deliberate failures failing correctly, and a final spot-check of 10 factual claims against generated reports or vanilla data. Report blockers honestly; do not invent results.
