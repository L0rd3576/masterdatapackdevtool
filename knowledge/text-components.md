# Text components, selectors, NBT paths, SNBT, coordinates (26.3)

Sources: corpus results (`generated/corpus-results.txt`), runtime test `tools/selftest/runtime_facts`,
`generated/reports/commands.json`, vanilla dialogs/advancements. Wiki notes marked (wiki).

## Text components
- In commands they are **SNBT** (since 1.21.5). JSON syntax is still accepted because JSON is valid SNBT.
  Verified OK: `tellraw @a {text:"a",color:"red",bold:true}`, `tellraw @a {"text":"json","color":"red"}`,
  `tellraw @a [{text:"a"},{text:"b",italic:true}]`, `tellraw @a "plain string"`,
  `tellraw @a {text:"score",extra:[{score:{name:"@s",objective:"c.obj"}}]}`.
- Events (renamed 1.21.5): `click_event:{action:"run_command",command:"/say hi"}`,
  `hover_event:{action:"show_text",value:"tip"}` - both verified OK.
  Field changes (wiki): open_url `value`->`url`; run/suggest_command `value`->`command`; change_page `value`->`page`;
  show_text `contents`->`value`; show_item/show_entity contents inlined.
- **Old `clickEvent` / `hoverEvent` are silently ignored** (server accepts the line; the event just does nothing).
  Vanilla 26.3 data never uses them. The linter flags them.
- Stored as compounds: summoning with `CustomName:{text:"Bob",color:"gold"}` stores `{color: "gold", text: "Bob"}`
  (runtime-verified). In item components: `custom_name={text:"X",italic:false}`.
- New-ish keys (wiki): `shadow_color`, `object` (atlas/sprite, player), click actions `show_dialog`, `custom`.

## Selectors
- `@p @a @r @s @e @n` (`@n` = nearest entity, since 1.21).
- Arguments: x y z distance dx dy dz scores tag team limit sort level gamemode name x_rotation y_rotation type nbt
  advancements predicate. Unknown option -> `Unknown option 'colour'`.
- Verified OK: `@e[type=minecraft:zombie,limit=3,sort=nearest]`, `@e[type=zombie]`, `@e[type=#minecraft:skeletons]`,
  `@e[type=!minecraft:player,distance=..10]`, `@e[type=minecraft:marker,tag=!keep,limit=5,sort=furthest]`,
  `@a[gamemode=!spectator,level=10..,x_rotation=-90..0]`, `@a[advancements={minecraft:story/root=true}]`,
  `@a[scores={c.obj=..0,c.trig=1}]`, `@e[nbt={OnGround:1b}]`, `@e[predicate=c:is_sneaking]`, `@a[name="Steve"]`.
- Unknown entity type -> `Invalid or unknown entity type`. A missing predicate in `predicate=` is NOT checked at load.
- Single-target arguments reject multi selectors at parse time (e.g. `tp @s @e[type=minecraft:pig]` BAD;
  `ride @s mount @e[type=minecraft:horse,limit=1]` OK).

## SNBT (wiki for 1.21.5 changes; basics verified via corpus)
- Types: `1b` byte, `1s` short, `1` int, `1L` long, `1.5f` float, `1.5`/`1.5d` double, `"str"`/`'str'`, `[..]` list,
  `[I;1,2]` int array, `{k:v}` compound. `true`/`false` = 1b/0b.
- 1.21.5 (wiki): heterogeneous lists allowed, trailing commas, `0x`/`0b` prefixes, `_` separators, unquoted strings
  cannot start with digit/`.`/`+`/`-`, functions `bool(x)`, `uuid(str)`.
- The server prints SNBT with spaces (`{a: 1, b: "x"}`); compare ignoring whitespace.

## NBT paths
- `a.b[0].c`, `Pos[1]`, `Inventory[{Slot:0b}]`, `Item.components."minecraft:custom_data".rf` (quote keys with `:`).

## Coordinates
- `~` relative, `^` local; never mix `^` with `~`/absolute (`Cannot mix world and local coordinates`).
- Block positions need integers (`setblock 0 0 0.5` -> `Invalid integer`).
- Integer x in entity positions is centred: `0 -60 0` -> x 0.5 (runtime-verified for x only).
- Rotation `<yaw> <pitch>`, `~` allowed, `^` not.
