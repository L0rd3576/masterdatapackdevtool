# Function macros, argument passing, return, recursion, context (26.3)

Every rule below is runtime-verified on the 26.3 server unless marked [W]. Evidence:
`tools/selftest/macro_facts/tests/{substitution,calls}.test.json` (part of `tools/selftest.py`) and probes run with
`tools/probe.py` on 2026-10-09 (scripts in `test-server/probe-*.txt`, not committed). Basic syntax: `functions.md`.

## Substitution: what `$(x)` becomes
| Argument value | Text inserted | Notes |
|---|---|---|
| `5`, `3s`, `7L`, `1b`, `true` | `5`, `3`, `7`, `1`, `1` | type suffix dropped |
| `1.5f`, `2.5d` | `1.5`, `2.5` | re-parsed as SNBT this is a **double** (`1.5d`) |
| `12345678.9d` / `1e10d` | `1.23456789E7` / `10000000000` | Java toString; the second is an invalid int -> error |
| `"a b"` | `a b` | strings are inserted **raw, without quotes** |
| `{a:1,b:"x y"}`, `[1,2]`, `[I;1,2]` | SNBT text `{a: 1, b: "x y"}` ... | inner strings stay quoted, so it round-trips |
- To get a string value back into data, quote it yourself: `$data modify storage x s set value "$(x)"`. This breaks if
  the string contains `"` (`Expected whitespace to end one argument`); use `'$(x)'` or pass the value via storage.
- Backslashes are inserted as-is (`'a\b'` -> `"a\b"` text).
- To pass whole values (items, text components, lists) prefer `data modify ... from storage` over `$(x)`.

## Calling
- `function f {k:v}`, `function f with storage|entity|block <src> [path]`. The `with` source must be a compound:
  list -> `Invalid argument type: LIST. Expected Compound`; missing path -> `Found no elements matching <path>`;
  non-container block -> `The target block is not a block entity`. With `entity` the compound is the entity NBT.
- Extra keys are ignored. A **non-macro** function called with arguments runs normally (args ignored).
- Function tags take arguments too: `function #ns:tag {x:7}` passes them to every function in the tag.
- A missing key: `Failed to instantiate function f: Missing argument v to function f`. **Nothing** in the
  function runs, including non-`$` lines before the bad line.
- A substituted line that does not parse (`v:"nan"` into a score) fails the same way:
  `Failed to instantiate function f: While instantiating macro f: Command '...' caused error: ...`; nothing runs.
- Top-level (console/RCON) the error text is the response. **Inside another function the failure is silent**:
  no log line, the caller continues with the next line. `execute store success ... run function f` stores 0.
  => test library functions with top-level calls; the harness's `expect_error` step proves the failure.
- Allowed names: `$(letters_digits_underscore)`; only lines starting with `$` are substituted (`functions.md`).

## return and results
- `return <int>` (negative allowed), `return fail` (stores 0 for both result and success), `return run <cmd>`.
- `execute store result score ... run function f` stores the `return` value; `return run function g {..}` passes
  g's return value through. `return` exits only the function it is in (caller continues).
- A function that ends **without** `return` stores nothing: `execute store result|success` leaves the target unset.
  Library functions that report a value therefore always end in `return`.
- `execute store result score X run scoreboard players add ...` stores the new total.

## Execution context
- `execute as/at/positioned ... run function f`: f inherits executor, position (and rotation/dimension) [W for rot].
- `schedule function` drops the context: runs with no `@s`, at the world spawn point (marker summoned with `~ ~ ~`
  landed at exactly `0.0 -60.0 0.0`, the flat-world spawn). Pass entity data via tags/scores/storage instead.
- `#minecraft:load` runs its values in the listed order (["a","b"] verified).

## Limits and errors
- `max_command_sequence_length` (default 65536) caps commands per function call chain, including nested calls.
  A self-recursive 2-line function stopped after **21845** iterations (65536/3: 2 commands + the call) with
  **no error or log line**. Long loops must be budgeted or spread over ticks (see `mcdp_lib:world/fill_spread`).
- Scoreboard division is floor division (`-7 / 2 = -4`, `-7 % 2 = 1`); division by zero fails ("Cannot divide by
  zero") and leaves the score unchanged.
- `execute store success ... run data modify X set from Y` is 0 when X already equals Y ("Nothing changed"):
  the library uses this as a generic equality test. `execute store result ... if data storage s list[]` = length.
- NBT compound matching on lists is subset matching: `s{next:["game"]}` matches `{next:["lobby","game"]}`.

## Other facts found while building library/mcdp_lib (runtime-verified by its tests or probes)
- NBT path: an index cannot be followed by a compound filter: `fe[-1]{c:1b}` -> load error `Invalid NBT path element`.
  `fe[-1].c` (incl. `execute store ... storage s fe[-1].c`) and `fe[{c:1b}]` are fine. Linter flags it now.
- `random value 4..4` -> runtime error `The range of the random value must be at least 1`; `random value 0..2147483646` works.
- Tick functions see the game time of the tick being processed minus one: an entry due at `time query gametime + N`
  read over RCON fires after N+1 steps, so `flow/after_as` stores `now + N - 1` (fires after exactly N ticks).
  `schedule function f 3t` fires after exactly 3 ticks (tests/flow.test.json).
- `item replace entity <armor_stand> armor.* with minecraft:air` reported "Replaced 1 slot(s)" and did not clear
  all armor slots inside a function; name slots explicitly. `with minecraft:air` on a named slot clears it.
- `item replace entity @s <slot> from entity <item_display> contents` copies an item with all components; `kill` of an
  item_display drops nothing (used for exact item restore). `/kill` of a chest_minecart drops its items + the cart.
- Mob effects NBT: `active_effects:[{id:"minecraft:speed",amplifier:1b,duration:-1,show_particles:0b,show_icon:0b}]`
  (`duration:-1` = infinite). `block_break_speed` attribute: zombies/armor stands "have no attribute".
- `execute store result ... run gamerule <bool rule>` stores 1/0; int rules store their value.
- `place template minecraft:igloo/top x y z` -> `Loaded template ...`; `minecraft:desert_well` is a folder, not a template.
- Scoreboard ops on an unset target (`operation #new obj += #x var`) treat it as 0 and create it.

## Performance (rough, wall time over RCON, 20 000-iteration loops, after JIT warm-up; noisy)
| Loop body | ms / 20k |
|---|---|
| plain `function` call | 12-13 |
| macro call, same args every time | 15 (48-85 before warm-up) |
| store score -> storage, then plain call | 20-34 |
| store score -> storage, then macro call with that changing arg | 49-145 |
So a macro call with changing arguments costs ~2-4x a plain call (~1.5 us extra); repeated identical arguments
look cached [unverified reason]. Rule: per-tick code over many entities uses scoreboard fast paths; macros are
fine for setup and for one call per tick.

## Argument-passing patterns (used by `library/mcdp_lib`)
- Small scalars/strings/selectors: macro compound `{name:"x",ticks:20}` or `with storage mcdp_lib:in`.
- Values, items, text, lists: put them in storage (`mcdp_lib:in <key>`) and pass only locations as macro args.
- Hot paths: fixed fake-player scores (`#a mcdp_lib.in`) in, `#result mcdp_lib.out` out, plus `return`.
- Loops with callbacks keep their state on a storage stack (`list[-1]`) so callbacks may nest loops.
- Callbacks receive data in `mcdp_lib:out` / `#index mcdp_lib.out`; read them at the start (nested calls overwrite).

## Library conventions seen in the community (not verified by server; for orientation only)
- Bookshelf: everything prefixed `bs.`, I/O storages `bs:in` / `bs:out`, objectives `bs.in` / `bs.out`, fake
  players to avoid clashes; per-module load tags. (glibs.readthedocs.io)
- Lantern Load: `#load:load` chain with pre_load/load/post_load; versions published as fake players on the
  `load.status` objective so dependants can check presence/version. (github.com/LanternMC/load)
- Adopted here: one prefix for every objective/tag/storage, `in`/`out` storages, fake players, version published as
  `#mcdp_lib load.status` (major*10000+minor*100+patch), library load listed first in `#minecraft:load`.
