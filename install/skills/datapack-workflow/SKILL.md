---
name: datapack-workflow
description: Use for any Minecraft Java 26.3 datapack task (writing .mcfunction files, loot tables, advancements, predicates, recipes, item components, tests). Gives the verified lookup -> write -> lint -> server-test procedure and the commands to run.
---

# Datapack workflow (Minecraft Java 26.3, data format 121)

## 1. Look up before writing (never from memory)
- Command grammar: `python tools/cmd_syntax.py <command> [subcommand ...]` (`--depth N` to limit).
- Known-good command forms: `knowledge/commands.md`; mistakes: `knowledge/pitfalls.md`.
- JSON shape: copy the closest vanilla file from `reference/vanilla-data/minecraft/<registry>/`.
  Find one: `grep -rl '"minecraft:set_count"' reference/vanilla-data/minecraft/loot_table | head -3`.
- IDs: `python -c "import json;print(sorted(json.load(open('generated/reports/registries.json'))['minecraft:item']['entries']))" | tr , '\n' | grep sword`
- Block states: `python -c "import json;print(json.load(open('generated/reports/blocks.json'))['minecraft:oak_stairs']['properties'])"`

## 2. Write
- New pack: copy `template-datapack/` (pack.mcmeta min/max_format 121, load/tick tags, example test).
- Folders are singular (`function/`, `loot_table/`, `tags/function/`). Namespace lowercase.
- Create objectives in the load function. No leading `/`. `execute ... run <cmd>`.
- 26.3 loot/predicates: `condition` (object), `modifier`, `"type": "minecraft:..."`; `sequence` keeps `functions`.

## 3. Lint after every edit
`python tools/lint_datapack.py <pack>` -> fix every ERROR (file:line and the token are printed).

## 4. Test on the real server before claiming done
Add `<pack>/tests/<feature>.test.json`:
```json
{"setup": ["scoreboard players set #n ns.obj 0"],
 "steps": [{"run": "function ns:thing"}, {"ticks": 20},
           {"assert_score": {"target": "#n", "objective": "ns.obj", "equals": 20}},
           {"assert": "if entity @e[type=minecraft:marker,tag=ns.m]"}]}
```
Run `python tools/run_tests.py <pack>`; it prints load errors verbatim and expected/actual for failed asserts.
Test world: flat, grass at y=-61, air from y=-60, chunks -32..31 forceloaded, time frozen except `{"ticks": N}`.

## 5. When the server and linter disagree
Server wins. Add the line to `tools/corpus/commands.txt` (or a JSON file to `tools/corpus/json/<registry>/`),
fix `tools/lint_datapack.py`, run `python tools/diff_corpus.py` until exit 0, and log it in `knowledge/lessons.md`.
