# .mcfunction files, macros, function tags (26.3)

Sources: server probes 2026-10-09, `tools/corpus/commands.txt` (+ `generated/corpus-results.txt`),
`tools/selftest/runtime_facts` (runtime-verified), `generated/reports/commands.json`.

## Syntax (verified)
- One command per line, **no leading `/`** (server: `Unknown or invalid command '/say slash' ... Do not use a
  preceding forwards slash`). Blank lines and `#` comment lines are ignored.
- Line continuation: a line ending in `\` is joined with the next; leading whitespace of the next line is dropped
  (`say a \` + `  b` printed `a b`).
- Each function is parsed at load. Only the **first** bad line per function is reported, and the whole function is
  then missing (`Unknown function ns:x` when called).
- Calls to functions that do not exist (`function ns:missing`, `execute if function ns:missing`) are **NOT reported
  at load** (silent no-op). The linter catches these.

## Function tags
- `data/minecraft/tags/function/load.json` -> run on world load and after `/reload`.
- `data/minecraft/tags/function/tick.json` -> run every game tick (not while `tick freeze` is active).
```json
{"values": ["example:load"]}
```
- Create every scoreboard objective in the load function (`scoreboard objectives add` is idempotent-ish: it fails
  harmlessly if the objective exists).

## Permission level
Functions run at `function-permission-level` (default 2 = "gamemasters"). Commands whose node requires "admins"
(3) or "owners" (4) are **unknown inside functions**: e.g. `tick`, `op`, `stop`, `ban`, `whitelist`
(server: `Unknown or incomplete command ... at position 0`). Check with:
`python -c "import json;c=json.load(open('generated/reports/commands.json'))['children'];print([k for k,v in c.items() if v.get('permissions',{}).get('permission',{}).get('level') in ('admins','owners')])"`

## Macros (verified at runtime)
```mcfunction
# data/rf/function/set_score.mcfunction
$scoreboard players set $(target) rf.v $(value)
```
- Call with a compound: `function rf:set_score {target:"#m",value:7}`
- Or from data: `function rf:set_score with storage rf:args a` (also `with entity <single> [path]`, `with block <pos> [path]`).
- Only lines starting with `$` are substituted; `$(name)` uses letters/digits/underscore. `$(bad name)` fails at
  load: `Can't parse function line 1`. A `$( ...` without a closing `)` fails the same way.
- A non-`$` line containing `$(x)` is NOT substituted (it parses as literal text).
- Calling a macro function without a required argument fails at runtime and runs nothing (verified).
- The substituted line is parsed when the macro runs, so macro lines can only be fully validated at runtime.

## return and results (verified at runtime)
- `return <int>`, `return fail`, `return run <command>`.
- `execute store result score #r obj run function ns:f` stores the function's `return` value (42 in the test).

## schedule (verified)
- `schedule function ns:f 5t` runs it exactly 5 ticks later (not after 4). Units: `t` ticks, `s` seconds, `d` days.
- `schedule function ns:f 1s append` (default mode replaces), `schedule clear ns:f`.

## Execution notes
- `#minecraft:tick` functions run as the server at world spawn; there is no `@s` unless you `execute as`.
- In 26.x the overworld has no permanently loaded spawn chunks (`Loading 0 persistent chunks`); use
  `forceload add` for areas a datapack must keep ticking without players.
- Gamerules limiting functions: `max_command_sequence_length`, `max_command_forks` (26.3 snake_case IDs).
