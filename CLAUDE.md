# Minecraft Datapack Master Workspace

You are launched from this folder no matter where the user's datapack project lives. The project path is added with `--add-dir`; edit files there, keep tools and knowledge here. Target: **Minecraft Java Edition 26.3** (data pack format **121.0**, Java 25) unless the user says otherwise.

## Core rule: your memory of datapacks is unreliable
Formats, command syntax, and registries change nearly every version, and 26.x postdates your training. Since 26.3 even loot tables changed (`functions`->`modifier`, `conditions`->`condition`, `function`/`condition`->`type`). Before writing any command or JSON, look it up in this order:
1. `generated/reports/` (commands.json, registries.json, blocks.json, datapack.json, minecraft/components/item/) and `reference/vanilla-data/minecraft/` (real 26.3 vanilla files: copy their shape).
2. `knowledge/` notes (each fact was verified; [W] marks wiki-only).
3. Official changelogs / Minecraft Wiki, then record what you learned in `knowledge/`.
Never state an unverified syntax as fact. If you cannot verify it, say so and log it in `knowledge/UNVERIFIED.md`.

## Tools (all Python 3 stdlib; run from this folder)
| Command | What it does |
|---|---|
| `python tools/cmd_syntax.py execute if` | Print exact 26.3 grammar for a command path (from commands.json) |
| `python tools/lint_datapack.py <pack>` | Static check: pack.mcmeta, folders, resource locations, JSON, every function line vs commands.json, registry IDs, references. Exit 1 on error |
| `python tools/run_tests.py <pack>` | Lint + boot a throwaway 26.3 server with the pack, fail on any load error, run `<pack>/tests/*.test.json` over RCON. Exit 1 on failure. Log: `test-server/last-run.log` |
| `python tools/diff_corpus.py` | Linter vs. real server on `tools/corpus/` (use when adding linter rules) |
| `python tools/selftest.py [--fast]` | Proves the harness: good packs pass, broken packs fail, 0 lint errors on all vanilla data |
| `python tools/verify_knowledge.py` | Re-checks knowledge/ claims against the generated reports |
| `python tools/new_project.py <ns> <dir> [--lib-prefix p]` | New pack from the template with the function library vendored (`--update <dir>` re-vendors) |
| `python tools/test_library.py` | Whole library suite: header/INDEX check, lint, server tests |
| `python tools/gen_library_index.py` | Regenerate `library/INDEX.md` from function headers (fails on a missing header) |
| `python tools/probe.py [--pack D] cmd...` | Research: boot a server, print raw responses to commands |
| `python tools/build_pack.py <project>` | Validate a minigame/map framework project (manifests in `minigames/ maps/ presets/ pool.json`) and compile it to a datapack |
| `python tools/mapgen/validate.py <project> [--maps]` | Schema + cross-ref check of all manifests (`--kind map <f>` for one file, `--config`) |
| `python tools/mapgen/report.py <maps/x.json>\|--project D` | Generate, run all map validators incl. real-server load, render PNG/ASCII to `build/mapgen/` |
| `python tools/mapgen/generate.py\|render.py\|gallery.py` | Single steps: .nbt + meta (`--hash`), renders, walk-through gallery (`--check`) |
| `python tools/mapgen/selftest_failures.py` | 3 broken fixtures (missing key, unreachable spawn, nondeterministic generator) must fail |
Test file format and test-world facts: `knowledge/testing.md`. A server boot takes about 7 s.

## Workflow for every task (mandatory)
1. Read the project's own `CLAUDE.md` and `pack.mcmeta` if present. New pack: copy `template-datapack/`.
2. Look up every command, component, folder, and JSON field before writing it (`cmd_syntax.py`, `knowledge/`, vanilla files). Never write from memory.
3. Write the smallest change that works.
4. Run `python tools/lint_datapack.py <project>` after every edit. Fix all ERRORs; read WARNs.
5. Add or update a test in `<project>/tests/` for new behavior, then run `python tools/run_tests.py <project>` before saying work is done.
6. Report what changed and what was verified, with real output. Never claim success without it.

## Function library (reuse before writing)
- `library/mcdp_lib/` is a tested library pack (110 public functions: score/math, timer, random, list, player, team,
  msg, item, world, rules, flow, fsm, debug). Before writing any helper function, search `library/INDEX.md`; call the
  library instead of re-writing command sequences. New packs: `tools/new_project.py` (vendors it).
- Missing something reusable? Add it to the library (header `#> mcdp_lib:<path>` + Purpose/Inputs/Outputs/Effects/
  Context/Cost/Example, a test in `library/mcdp_lib/tests/`), then `tools/gen_library_index.py` and
  `tools/test_library.py`. Procedure and conventions: skill `function-library`; macro rules: `knowledge/function-macros.md`.

## Ground truth layout
- `server/server.jar` (26.3, sha1 33680f5f...), `runtime/jre25/` (Temurin 25), `generated/` (data generator output, `--all`).
- `reference/vanilla-data/minecraft/` vanilla data extracted from the jar (no functions; use for JSON shapes).
- `test-server/template/server.properties` base config for test servers; `test-server/runs/` is temporary.
- To regenerate after a version change: download the jar via the version manifest, then
  `cd server && ../runtime/jre25/bin/java -DbundlerMainClass=net.minecraft.data.Main -jar server.jar --all --output ../generated`,
  re-extract `data/minecraft/` from `server/versions/<v>/server-<v>.jar`, delete `generated/lint-cache.json`, run `tools/selftest.py`
  and `tools/diff_corpus.py`, update `DATA_FORMAT` in `tools/lint_datapack.py`.

## Self-improvement (required, every session)
This is how you get better over time; nothing is retrained, so the learning lives in these files.
- **Any mistake** (yours, found by the linter, a server error, or a user correction): before finishing, append an entry to `knowledge/lessons.md`: date, what went wrong, the verified correct form, how to avoid it. Keep entries 3-5 lines.
- **New verified fact** about 26.3: put it in the matching `knowledge/<topic>.md` with a source (file in `generated/`, changelog, or a passing test). If it is checkable from reports, add a claim to `tools/verify_knowledge.py`.
- **Repeated pattern** (same kind of task or mistake 2+ times): create or update a skill in `.claude/skills/<name>/SKILL.md` here (e.g. `mcfunction-macros`, `custom-items`, `scoreboard-timers`). A skill holds the verified procedure, a working example, and the pitfalls. Keep each skill under 150 lines.
- **Linter gap**: if the server rejects something the linter passed, fix `tools/lint_datapack.py` and add the failing line to `tools/corpus/commands.txt` (or a file to `tools/corpus/json/`), then run `python tools/diff_corpus.py` until it exits 0.
- Consolidate occasionally: merge duplicate lessons and delete ones that a skill or linter rule now covers. Do not let `lessons.md` exceed about 200 lines.
- Tell the user in one line what you saved.

## Rules
- Do not edit anything under `%APPDATA%\.minecraft\saves` unless the project lives there and the user asked. Test only on throwaway servers in `test-server/`.
- Ask before downloads over 50 MB.
- Follow the global usage-efficiency rules (`~/.claude/CLAUDE.md`): lowest model/effort that works, filtered output, small reads. Do not open `blocks.json` (7 MB) or `commands.json` directly; query them with a one-line Python command or `tools/cmd_syntax.py`.
- Edit code with the Edit tool, not scripted string replacement (escapes get mangled; see lessons.md).

## Index
- `knowledge/pack-format.md` pack.mcmeta, format 121, what the server does with old forms
- `knowledge/datapack-structure.md` folders (singular), namespaces, tags, load behavior, silent ignores
- `knowledge/functions.md` mcfunction syntax, macros, return, schedule, permission level, function tags
- `knowledge/function-macros.md` macro substitution/call/failure rules, return, context, limits, performance (tested)
- `library/INDEX.md` reusable function index; `library/mcdp_lib/` the library pack + tests
- `knowledge/commands.md` server-verified command forms, renamed gamerules, new 26.x commands (`/compute`, slot sources)
- `knowledge/item-components.md` `id[component=value]`, item predicates, item NBT shape, component list
- `knowledge/text-components.md` SNBT text, click_event/hover_event, selectors, SNBT, NBT paths, coordinates
- `knowledge/loot-predicates.md` 26.3 loot/predicate/modifier renames, number providers
- `knowledge/advancements.md`, `knowledge/recipes.md`, `knowledge/registries.md` (how to look up IDs)
- `knowledge/changes-since-1.21.md` breaking changes 1.21 -> 26.3 ([V] verified / [W] wiki)
- `knowledge/pitfalls.md` 42 verified mistakes and which ones are silent
- `knowledge/testing.md` test file format, test world, harness self-checks
- `knowledge/lessons.md` running lessons; `knowledge/UNVERIFIED.md` open questions; `knowledge/_research/` raw wiki notes
- `knowledge/mapgen.md` structure format, size limits, placement, arena dimension, movement values, fake players
- `knowledge/framework-contract.md` minigame/map/preset/pool manifests, defaults, what build_pack emits, round flow
- `knowledge/map-style.md` approved map aesthetic (read before authoring maps)
- `schemas/` JSON schemas for every manifest + `tools/mapgen/config.json`; `examples/slice/` working framework project
- `tools/mapgen/` generators/ + validators/ are plugins (add a file, never edit core); `tools/framework/pack/` round logic
- `.claude/skills/` skills learned over time (map-authoring, minigame-manifest, generator-plugin are in
  `install/skills/` until copied, see `install/README.md`); `template-datapack/` valid starter pack with a test
- `claude-code-prompt.md` the bootstrap prompt that built all of the above
