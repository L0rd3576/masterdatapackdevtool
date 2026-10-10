---
name: function-library
description: Use when writing or reviewing mcfunction code for a Minecraft 26.3 datapack (timers, cooldowns, random picks, lists, teams, messages, kits, region fills, game rules, state machines, logging), when starting a new datapack project, or when adding a reusable function. Finds and calls the tested mcdp_lib library instead of re-writing command sequences.
---

# Reusing and extending mcdp_lib (Minecraft Java 26.3)

Workspace: `C:\Users\lrafy\mc-datapack-tools`. Library pack: `library/mcdp_lib/`. Index: `library/INDEX.md`.

## 1. Before writing any helper: search the index
```
grep -i "cooldown\|timer" library/INDEX.md
```
Each line: `` `mcdp_lib:<path>` `{macro args}` [**fast**] - purpose ``. Open the function file for the full header
(Inputs, Outputs, Effects, Context, Cost, Example). Never call `mcdp_lib:_internal/*`.

## 2. Use it in a project
- New project: `python tools/new_project.py <ns> <dir>` (vendors the library as `data/mcdp_lib/`, lists its load/tick
  first). Own prefix: `--lib-prefix <ns>_lib` (renames every function/objective/storage). Existing pack:
  `python tools/new_project.py --update <dir>` re-vendors (also used to upgrade; lint WARNs on a version mismatch).
- Calling conventions:
  - Macro args inline `function mcdp_lib:random/int {min:1,max:6}` or `... with storage my:args path`.
  - Payloads (values, items, text components) go in storage `mcdp_lib:in <key>`: `value` (list/*), `item`
    (item/*_from_storage), `text`/`title`/`subtitle` (msg/*), `rules` (rules/apply), `fsm` (fsm/define).
  - Results: `return` value (use `execute store result ...`), `#result mcdp_lib.out`, `mcdp_lib:out <key>`.
  - **fast** functions read scores `#a #b #value #min #max` on `mcdp_lib.in` (no macro; safe per tick).
  - Callbacks are function ids (strings). Loop callbacks read `mcdp_lib:out foreach.item` / `#index mcdp_lib.out`
    first (nested loops overwrite them); compound list items are also passed as macro args.
- Lint checks every call to a macro function: missing keys in an inline `{...}`, calls without args, `if function` /
  `schedule function` on a macro function (they cannot pass args). A missing key at runtime runs nothing and is
  **silent when nested**, so trust the linter and top-level tests.

## 3. Adding a function to the library (when something reusable is missing)
1. Look up every command (`tools/cmd_syntax.py`, `knowledge/`); check `knowledge/function-macros.md` for macro rules.
2. File `library/mcdp_lib/data/mcdp_lib/function/<category>/<name>.mcfunction`, header exactly:
```mcfunction
#> mcdp_lib:<category>/<name>
#> Purpose: one sentence.
#> Inputs: macro {a:int, b:string}; storage mcdp_lib:in value      (every $(name) must appear here)
#> Outputs: return ...; score #result mcdp_lib.out / storage mcdp_lib:out ...
#> Effects: what changes in the world/storage
#> Context: any | as an entity (@s) | at ...
#> Cost: fast (scoreboard only) | macro (setup) ...
#> Example: function mcdp_lib:<category>/<name> {a:1,b:"x"}
```
3. Helpers go in `function/_internal/<category>/`. Internal temp scores: `mcdp_lib.var`; storage `mcdp_lib:internal`.
   Objectives are created in `_internal/load` (idempotent; keep config across /reload).
4. Always end with `return` when reporting a value (a function without `return` leaves `execute store` targets unset).
5. Test: add steps to `library/mcdp_lib/tests/<category>.test.json`; call the function **top-level** (nested
   macro failures are silent); add an `{"run": ..., "expect_error": "Missing argument x"}` step. Test-only callbacks
   live in `data/mcdp_lib_test/` (not vendored). No players exist on the test server: test on markers/armor stands.
6. `python tools/gen_library_index.py` then `python tools/test_library.py` (must PASS); bump the version in
   `_internal/load` (`mcdp_lib:meta version`, `#mcdp_lib load.status` = major*10000+minor*100+patch) on API changes.

## Pitfalls (all verified, see knowledge/function-macros.md)
- Strings substitute **without quotes**; numbers lose their suffix (`1.5f` -> `1.5`, re-parsed as double). Quote
  strings yourself (`"$(x)"`), and keep `"` out of such strings.
- `list[-1]{k:1b}` is an invalid NBT path (load error); test a field: `list[-1].k`.
- `random value 4..4` errors at runtime; `mcdp_lib:random/int` handles min = max.
- Recursion is capped by `max_command_sequence_length` (65536 commands per call chain), silently. Loops over big
  lists/areas: spread over ticks (`world/fill_spread`) or cap (`flow/repeat` uses `mcdp_lib:config max_repeat`).
- `schedule function` drops @s and runs at world spawn; use `flow/after_as` to keep the entity.
- Bool command args (`friendlyFire`, `effect ... hideParticles`) need `true/false`, but `1b` substitutes as `1`:
  branch on a score instead (see `team/setup`).
- `block_break_speed` exists only on players; mobs/armor stands report "has no attribute".
