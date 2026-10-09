# Testing datapacks on a real 26.3 server

`python tools/run_tests.py <pack>` = lint + boot a throwaway server with the pack + run `<pack>/tests/*.test.json`
over RCON. Exit 0 only if everything passes. Server log of the last run: `test-server/last-run.log`.
Options: `--keep` (keep `test-server/runs/run-*`), `--skip-lint`, `--only <substring>`.

## Test file format (`<pack>/tests/<name>.test.json`)
```json
{
  "description": "what this proves",
  "setup":    ["scoreboard players set #n t.ticks 0", "summon minecraft:marker 0 -60 0 {Tags:[\"t.m\"]}"],
  "steps": [
    {"run": "function t:main"},
    {"run": "function t:needs_args", "allow_error": true},
    {"run": "data get storage t:s x", "expect_contains": "5"},
    {"ticks": 5},
    {"assert": "if score #n t.ticks matches 5", "show": "scoreboard players get #n t.ticks"},
    {"assert_score": {"target": "#n", "objective": "t.ticks", "equals": 5}},
    {"assert_data": {"source": "entity @n[type=minecraft:marker]", "path": "Pos[0]", "equals": "5.5d"}},
    {"assert_output": {"command": "data get storage t:s list", "contains": "1", "matches": "regex", "equals": "full text"}}
  ],
  "teardown": ["kill @e[type=minecraft:marker]"]
}
```
- `assert` runs `execute <condition>`; passes if the response starts with `Test passed`.
- `assert_data` compares the SNBT after `...data: ` ignoring whitespace outside strings (server prints `{a: 1}`).
- A `run` step fails if the response is a parse error (`<--[HERE]`, `Unknown or incomplete command`,
  `Unknown function`, `Incorrect argument`, ...). Runtime failures like "No entity was found" are not errors:
  assert on the effect instead.
- After each test, new ERROR/WARN lines in the server log fail the test.
- Steps run from the server console (RCON): no `@s`; use `execute as ... run`. Max 1446 bytes per command.

## World the runner gives you (verified)
- Flat world: bedrock y=-64, dirt -63..-62, grass_block y=-61, air from y=-60. Chunks -32..31 (x,z) forceloaded.
- Before tests: `tick freeze` (time only advances via `{"ticks": N}` = `tick step N`, waits until done),
  `advance_time`/`advance_weather`/`spawn_*` gamerules false. `#minecraft:tick` functions run only during steps.
- `#minecraft:load` already ran at startup; scoreboards/storage persist across tests in one run (reset in `setup`).
- 26.3 `pause-when-empty-seconds` defaults to 60 (server stops ticking with no players): the template sets 0.

## Checking load errors only
A pack with no tests still gets the lint + load check. Load errors fail the run and are printed verbatim, e.g.
`[ServerMain/ERROR]: Failed to load function t:main ... Whilst parsing command on line 2: Incorrect argument ...`.

## Harness self-checks
- `python tools/selftest.py` (all; ~2 min) or `--fast` (linter only): good packs PASS, broken packs FAIL,
  and the linter reports 0 errors on all 8266 vanilla data files.
- `python tools/diff_corpus.py [--show-all]`: linter vs server on `tools/corpus/commands.txt` and
  `tools/corpus/json/**` (~1 min, two server boots). Exit 1 = a linter gap or false positive. Add a line here
  whenever the server rejects something the linter passed (`## lint-only` = silent server bug the linter must flag,
  `## server-only` = argument types the linter only checks shallowly).
- `python tools/verify_knowledge.py`: re-checks factual claims in knowledge/ against the generated reports.
