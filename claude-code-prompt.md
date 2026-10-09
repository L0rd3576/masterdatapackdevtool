# Prompt for Claude Code: build a Minecraft 26.3 datapack knowledge base and test harness

Paste everything below the line into Claude Code, run from `C:\Users\lrafy\mc-datapack-tools`.
Suggested launch: `claude --model opus --effort high` (use plan mode first, then approve).

---

You are setting up a durable environment so that future Claude Code sessions write **correct Minecraft Java Edition 26.3 datapacks on the first try** and can **verify their work by running it**. Past sessions made many syntax and format mistakes and only caught them after the fact. Your job is to remove the guesswork.

## Ground rules
- Target version: **Minecraft Java Edition 26.3**. Your training data predates this version and the 26.x naming scheme. Treat your memory of datapack formats, command syntax, and registries as **unreliable**. Every claim you write down must be traced to a source you actually read this session, not recalled.
- Source priority: (1) the real 26.3 server jar and its generated reports, (2) official Minecraft changelogs and Minecraft Wiki pages for 26.1 to 26.3 and the versions before them, (3) community docs. If sources disagree, the jar wins.
- Never write "I believe" content into the knowledge base. If something cannot be verified, list it under `UNVERIFIED` in the notes instead of stating it as fact.
- Ask before downloading anything over 50 MB or installing software outside `C:\Users\lrafy\mc-datapack-tools`.
- Do not modify anything under `%APPDATA%\.minecraft\saves` except by explicit instruction. Run tests against a throwaway server directory only.

## Phase 1: Get ground truth from the game itself
1. Obtain the official **26.3 server jar** from Mojang's version manifest (`https://piston-meta.mojang.com/mc/game/version_manifest_v2.json`) and a matching **Java runtime** (check the version JSON's `javaVersion` field for the required major version). Put them in `server/` and `runtime/`.
2. Run the built-in data generator: `java -DbundlerMainClass=net.minecraft.data.Main -jar server.jar --all --output generated` (verify the exact flags with `--help`). Keep `generated/reports/commands.json`, `registries.json`, `blocks.json`, `items.json`, and the data component and tag listings. These are the authoritative command grammar and registry IDs for 26.3.
3. Extract the vanilla datapack from the jar (`data/minecraft/...`) into `reference/vanilla-data/`. Real vanilla advancements, loot tables, predicates, recipes, and function tags are the best examples of correct current formats.
4. Record the exact **pack format number(s)** and the exact `pack.mcmeta` structure for 26.3 (including any `min_format`/`max_format` or `supported_formats` style fields, and whether the version uses a major.minor scheme). Confirm from the jar's `version.json` and the changelogs, not memory.

## Phase 2: Read the documentation thoroughly
Read, do not skim, and write structured notes to `knowledge/` (one file per topic). For each topic record: the rule, a minimal correct example copied from vanilla data or verified by a test, and the old/deprecated form that must NOT be used.

Cover at least:
- Datapack structure: folder names (watch for singular vs plural renames across versions), namespaces, resource location rules and allowed characters, `pack.mcmeta`, overlays, load order, `/reload` behavior.
- Function files: `.mcfunction` syntax, comments, line continuation rules, macros (`$` lines), `function` tags (`#minecraft:tick`, `#minecraft:load`), execution order and tick timing, recursion and command-limit gamerules.
- Command grammar for every command used in datapacks: `execute` (all subcommands, `store`, `if/unless` variants), `scoreboard`, `data`, `item`, `summon`, `give`, `tag`, `team`, `bossbar`, `attribute`, `effect`, `particle`, `playsound`, `return`, `schedule`, `tellraw`/`title`, `fill`/`setblock`/`clone`, `random`, `tick`, `place`, `damage`, `rotate`, `ride`, etc. Use `commands.json` as the source for argument structure.
- **Data components** and the item stack format used in commands and loot tables. This changed heavily from NBT in 1.20.5 and has kept changing. Document the current syntax for `give`, `item replace`, `/summon` with item entities, predicates, and `custom_data`.
- Text components (JSON text format changes, SNBT vs JSON usage in commands), selectors and their arguments, NBT paths, SNBT syntax, coordinates and rotation.
- Registries and **tags**: block, item, entity type, damage type, enchantment, etc., with the exact folder each lives in.
- Advancements, loot tables, predicates, item modifiers, recipes, enchantments, damage types, dimension/worldgen JSON, trims, jukebox songs, painting variants, and any new data-driven registries in 26.x. For each, list required fields and valid trigger/condition/function names.
- Features added or changed from 1.21 through 26.3 that affect datapacks. Read every official changelog in that range and write `knowledge/changes-since-1.21.md` listing breaking changes (renames, removed commands, changed argument order, moved folders, format bumps).
- Common mistakes. Build `knowledge/pitfalls.md` from your findings, including: using removed NBT item syntax, wrong folder names, wrong pack format, missing namespace, trailing slashes, invalid resource location characters, running `execute` without `run`, selector scope mistakes, storing to the wrong score target, forgetting `as @s`/`at @s`, scoreboard objectives not created in the load function, and anything else you find.

## Phase 3: Make mistakes impossible to miss (static checking)
Build `tools/lint_datapack.py` (Python 3 stdlib only; Python 3.14 is installed) that checks a datapack directory and exits non-zero on any error. At minimum:
- Valid `pack.mcmeta` with the correct 26.3 format fields.
- Directory names match the 26.3 layout (flag old/renamed folders with a message saying what the new name is).
- Resource location validity (lowercase, allowed characters) for every file path and every reference in JSON and functions.
- Every `function ns:path` and `#tag` reference resolves to a file that exists.
- JSON files parse, and use the correct top-level fields for their type.
- Parse every `.mcfunction` line against `commands.json` (build a small grammar walker). Report file, line number, and the first token that fails to parse. Handle `execute` recursion and `$` macro lines (validate after substituting dummy values).
- Unknown registry IDs (blocks, items, entities, effects, etc.) checked against `registries.json`.
The linter is a fast first pass. The server in Phase 4 is the final authority; the linter must never claim a pack is valid when the server rejects it. When they disagree, fix the linter and add a regression test.

## Phase 4: Run the pack in a real server (functional testing)
Build `tools/run_tests.py` and a `test-server/` template:
1. Create a clean server directory per run, with `eula=true`, `online-mode=false`, `server.properties` set for fast headless tests (flat world, no mobs spawning unless needed, small view distance, `enable-rcon=true` with a random local-only password, `gamerule` defaults documented). Start from the downloaded jar; shut down cleanly after the run.
2. Copy the datapack under test into the world's `datapacks/` folder and start the server. **Parse the server log for datapack load errors** (parsing failures, unknown functions, invalid JSON, registry errors). Any such error fails the run and is printed verbatim.
3. Connect over RCON and execute test scenarios. Define tests in simple files, e.g. `tests/<name>.test.json` or `.mcfunction`-based:
   - setup commands (summon, setblock, scoreboard setup),
   - actions (`function ns:thing`, `time add`, `tick step`/`tick freeze` to advance deterministic ticks),
   - assertions using `execute if/unless ...` plus `return`/scoreboard checks, `data get` comparisons, or `execute if entity`.
   A failing assertion must print the expected and actual values.
4. Return a clear pass/fail summary and a non-zero exit code on failure. Also capture the server log to `test-server/last-run.log`.
5. Add a `--watch`-free, one-command entrypoint: `python tools/run_tests.py <path-to-datapack>`.
6. Write 3 to 5 self-tests proving the harness works: a deliberately broken pack must FAIL (bad command, bad JSON, missing function) and a known-good pack must PASS. Run them and show real output.

## Phase 5: Package it for future sessions
- `C:\Users\lrafy\mc-datapack-tools\CLAUDE.md` and `mcdp.cmd` already exist. EXTEND CLAUDE.md (keep its Self-improvement section and rules; fix any paths) instead of rewriting it. Keep it under 200 lines with: the exact target version, how to run the linter and tests, a mandatory workflow ("look up syntax in `knowledge/` and `generated/reports/` before writing, run the linter after every edit, run tests before saying work is done, never claim success without real tool output"), and an index of the knowledge files.
- Create a user-level snippet at `C:\Users\lrafy\.claude\rules\minecraft-datapacks.md` that tells Claude Code, in any project containing a `pack.mcmeta`, to follow that workflow and where the tools live (absolute paths).
- Create a project template `template-datapack/` (correct `pack.mcmeta`, load/tick function tags, example function, example test) so new packs start valid.
- Add `knowledge/UNVERIFIED.md` listing anything you could not confirm.

## Definition of done
Do not stop at writing files. Finish only when you have **run** and shown real output for:
1. the data generator producing the reports,
2. the linter passing on `template-datapack/` and failing on a broken pack,
3. the test runner passing on the template and failing on a broken pack,
4. a final self-review where you re-check at least 10 factual claims in `knowledge/` against the generated reports or vanilla data and report any you had to correct.

Report blockers honestly. If a step fails (download, Java, RCON), say so and try an alternative rather than inventing output.
