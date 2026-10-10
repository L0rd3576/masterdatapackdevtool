---
name: map-authoring
description: Use when creating, generating, reviewing, or fixing a minigame map for a Minecraft 26.3 framework project (maps/<id>.json, generated or hand-made .nbt structures, spawns, markers, renders, the gallery). Gives the write -> generate -> validate -> render+review -> server test -> pool -> gallery loop.
---

# Map authoring loop (tools/mapgen, Minecraft Java 26.3)

Workspace `C:\Users\lrafy\mc-datapack-tools`. Facts: `knowledge/mapgen.md`. Contract: `knowledge/framework-contract.md`.
Style the user approved: `knowledge/map-style.md` (read it first, so a new map needs little direction).
Working examples: `examples/slice/maps/*.json`.

## Loop (repeat until every step is clean)
1. **Write the manifest** `<project>/maps/<id>.json`. Copy the shape from an example and check keys in
   `schemas/map.schema.json`. Required: id (= file name), display_name, tags, players {min,max}, source.
   For a generator, check its `PARAMS_SCHEMA` (top of `tools/mapgen/generators/<name>.py`). Omitted params use the
   defaults. Leave `seed` out while exploring.
2. **Validate the schema**: `python tools/mapgen/validate.py --kind map <project>/maps/<id>.json`.
3. **Generate + offline validators**: `python tools/mapgen/report.py <project>/maps/<id>.json --no-server`
   (bounds, spawn count, ground, hazards, reachability, markers, void gaps, determinism, build budget).
   Explore variants with `generate.py <manifest> --seed N --render`. Write the chosen seed into `source.seed`.
4. **Review the render**: Read `build/mapgen/<id>.top.png` with the Read tool (actually look at it). Check
   `<id>.layers.txt` for the walk layer (y=1): `S` spawn, `O` objective, `#` solid, `.` air inside the map,
   space = untouched void. Look for spawns hugging walls, dead ends, unfair spawn clusters, and huge empty space.
5. **Server test**: `python tools/mapgen/report.py <manifest>` (no `--no-server`). The `server_load` line must PASS.
6. **Fix and repeat**: change params or seed, or add `spawns`/`markers` overrides. Never relax validator
   thresholds just to pass. If one map really needs it, use the manifest `validation` block and say why in
   `description`.
7. **Add to the pool**: add `{"id": ..., "weight": 1}` to `pool.json` maps. Then run
   `python tools/mapgen/validate.py <project> --maps` (the map must fit at least one minigame's tags and player range).
8. **Build + test**: `python tools/build_pack.py <project>`, `python tools/lint_datapack.py <out>`,
   `python tools/run_tests.py <out>`.
9. **Gallery**: `python tools/mapgen/gallery.py <project> --check` (every map + 3 labels each). In game:
   `/function <ns>:gallery/build`, wait 1 s, then `/function <ns>:gallery/tp`.
10. **Record taste**: if the user approves or corrects a map, add one line to `knowledge/map-style.md`.

## Pitfalls
- Spawns are local cells where the player's feet are (floor y + 1), not the floor block.
- A spawn on a slab or wall top is "not standable" (spawn_ground) and usually unreachable.
- Drops > `movement.max_drop` are one-way. Mutual reachability fails on them on purpose.
- Hand-made `.nbt`: the determinism check is skipped for it, but every other validator still runs. Make sure
  `fill_air` is true or restore leaves debris (the framework restores by re-placing tiles).
- Entities summoned into a chunk that was just forceloaded can vanish. Wait `gallery.place_delay_ticks` first.
- Nothing about players comes from the map except spawns and markers. Rules belong to the minigame manifest.
