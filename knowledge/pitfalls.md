# Pitfalls (26.3) - each one verified this session unless marked (wiki)

"Silent" = the server loads without any error, the feature just does not work. The linter catches every item
marked [lint]; the test runner catches the rest only if a test exercises the behaviour.

## Pack and folders
1. Plural folders (`functions/`, `loot_tables/`, `tags/functions/`, `tags/items/`) - **silent** [lint].
2. Uppercase or invalid characters in namespace/path (`data/MyPack/`, `My Func.mcfunction`) - **silent** [lint].
3. `pack.mcmeta` with only `pack_format` - loads with a WARN [lint, runner]. Use `min_format`/`max_format` = 121.
4. No `pack.mcmeta` - pack ignored (`Found non-pack entry`) [lint, runner].
5. A format range that excludes 121 still loads on a dedicated server (client shows incompatible) [lint].
6. `worldgen/configured_feature/` (26.3 is `worldgen/feature/`, config inline) [lint].

## Functions
7. Leading `/` - load error [lint].
8. `execute ... <command>` without `run` - load error, whole function dropped [lint].
9. Calling a missing function (`function ns:typo`, `execute if function`, `schedule`) - **silent** [lint].
10. Function tag listing a missing function - tag dropped, so *none* of its functions run (load still continues) [lint].
11. Objectives not created in the load function -> `Unknown scoreboard objective` at runtime.
12. `tick`, `op`, `stop`, `ban`... in functions - unknown command (permission level 3/4 > 2) [lint].
13. Macro `$(...)` on a line without leading `$` - not substituted (literal text; verified) [lint warning].
14. Macro function called without all keys - runtime error, nothing runs.
15. (not server-tested) `@s` in `#minecraft:tick`/`load` functions is the server (nothing) - use `execute as @a at @s run ...`.
16. (not server-tested) Forgetting `at @s`: `execute as @a run setblock ~ ~ ~ ...` uses the *original* position, not each player's.
17. Old gamerule names (`doDaylightCycle`, `keepInventory`) - load error [lint]. Use `advance_time`, `keep_inventory`.

## Items / components / NBT
18. Item NBT after the id (`diamond_sword{Damage:5}`) - load error [lint]. Use `[damage=5]`.
19. `enchantments={levels:{...}}`, `attribute_modifiers={modifiers:[...]}`, `show_in_tooltip` - pre-1.21.5 [lint].
20. `{"item": ...}` in recipe ingredients/results or advancement icons - rejected [lint]. Use strings / `"id"`.
21. Entity NBT `ArmorItems`/`HandItems` - gone; use `equipment:{head:..., mainhand:...}` (runtime-verified).
22. Item stacks in NBT use `id`, `count`, `components` (not `Count`, `tag`).
23. `villager.N` slots - gone, use `mob.inventory.N` (server rejects).
24. Attribute `generic.max_health` - use `max_health` [lint].
25. Particle options as positional numbers (`dust 1 0 0 1`) - use SNBT `dust{color:[1.0,0.0,0.0],scale:1.0}` [lint].

## Text
26. `clickEvent`/`hoverEvent` - **silent** (ignored) [lint]. Use `click_event:{action:"run_command",command:"/..."}`.
27. Text components are SNBT objects, not JSON strings inside quotes: `CustomName:{text:"Bob"}`, not `'{"text":"Bob"}'`.

## Loot tables / predicates / item modifiers (26.3)
28. `functions` / `conditions` keys - **silently ignored** in loot tables [lint]. Use `modifier` / `condition`.
29. `{"condition": "minecraft:x"}` / `{"function": "minecraft:x"}` objects - rejected [lint]. Use `"type"`.
30. Top-level JSON list as a predicate or item modifier file - rejected [lint]. Use `all_of` / `sequence`.
31. `minecraft:sequence` still needs `functions` (not `modifier`) [lint].
32. Misspelled required field (`chanse`) - rejected (server stops loading) [lint flags near-miss keys].
33. Any JSON error in an element file stops the whole server from starting (not just that file).

## Advancements
34. Root advancement (no `parent`) with `display` needs `display.background` - rejected [lint].
35. `rewards.function` to a missing function - **silent** [lint].

## Selectors / coordinates / scores
36. Single-target arguments with `@e`/`@a` and no `limit=1` - load error [lint].
37. `@e` where only players are allowed (e.g. `give @e ...`) - load error [lint].
38. Mixing `^` with `~` - load error [lint]. Decimal block coordinates - load error [lint].
39. Objective/holder names with characters outside `A-Za-z0-9_.+-` - load error [lint].
40. `scoreboard objectives add x <criterion>` with a typo - load error [lint].

## Test environment
41. 26.3 servers pause when empty after 60 s (`pause-when-empty-seconds`) - the test template sets 0.
42. No spawn chunks since 1.21.9 - forceload what you need (the runner forceloads -32..31).
