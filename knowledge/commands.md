# Commands in 26.3 - verified forms

Authoritative grammar: `python tools/cmd_syntax.py <command> [subcommand...]` (reads generated/reports/commands.json).
Every example marked OK below was accepted by the 26.3 server inside a function (corpus run, see
`generated/corpus-results.txt`); every BAD line was rejected (message shown) or is a silent bug.

## execute
- `execute as @a at @s run say hi` OK. `execute as @a say hi` BAD (`Incorrect argument`): needs `run`.
- Subcommands: align anchored as at facing if in on positioned rotated run store summon unless.
- `execute if|unless`: biome block blocks data dimension entity function items loaded predicate score slots stopwatch.
- OK: `execute if score #a c.obj matches 1..5 run ...`, `execute if score #a c.obj > #b c.obj run ...`,
  `execute if block ~ ~-1 ~ #minecraft:logs run ...`, `execute if block ~ ~ ~ minecraft:oak_stairs[facing=north,half=top] run ...`,
  `execute if items entity @s weapon.mainhand minecraft:diamond_sword run ...`,
  `execute if items entity @s container.* #minecraft:swords run ...`,
  `execute if items entity @s weapon.mainhand *[minecraft:custom_data~{c:{id:1}}] run ...`,
  `execute if slots entity @s container.*`, `execute if function c:helper run ...`, `execute if entity @s` (no run: just a test),
  `execute store result score #a c.obj run data get storage c:s value`,
  `execute store result storage c:s value int 1 run scoreboard players get #a c.obj`,
  `execute store result entity @s Health float 1 run ...`, `execute positioned over world_surface run ...`,
  `execute anchored eyes positioned ^ ^ ^1 run ...`, `execute on passengers|attacker run ...`,
  `execute summon minecraft:marker run tag @s add c.m`.
- BAD: `execute run` (`Unknown or incomplete command`). `execute align xzy` is OK (any order of x, y, z).

## scoreboard
- OK: `scoreboard objectives add c.obj dummy`, `... add c.obj2 dummy {text:"Display"}`, `... trigger`, `... deathCount`,
  `... minecraft.mined:minecraft.stone`; `scoreboard players set|add|remove|reset|get|enable|operation|display name`.
- Objective/holder names: `[A-Za-z0-9_.+-]`. BAD `Bad!Name` (`Expected whitespace ... trailing data`).
- BAD `scoreboard objectives add c.x not_a_criterion` (`Unknown criterion`). BAD operation `><=` (`Invalid operation`);
  valid: `= += -= *= /= %= < > ><`.
- Fake players `#name` are fine as score holders; `*` = all holders (reset).

## gamerule (renamed in 1.21.11; registry IDs, snake_case)
- OK: `gamerule spawn_mobs false`, `gamerule keep_inventory true`. Also accepted with `minecraft:` prefix.
- BAD: `gamerule doDaylightCycle false`, `gamerule keepInventory true` (`Incorrect argument`).
- Map: doDaylightCycle->advance_time, doWeatherCycle->advance_weather, doMobSpawning->spawn_mobs,
  keepInventory->keep_inventory, mobGriefing->mob_griefing, doFireTick->(removed; fire_spread_radius_around_player),
  randomTickSpeed->random_tick_speed, commandBlockOutput->command_block_output, sendCommandFeedback->send_command_feedback,
  doImmediateRespawn->immediate_respawn, doInsomnia->spawn_phantoms, doMobLoot->mob_drops, doTileDrops->block_drops,
  naturalRegeneration->natural_health_regeneration, maxCommandChainLength->max_command_sequence_length.
  Full list: `python tools/cmd_syntax.py --depth 1 gamerule`.

## data / storage
- OK: `data modify storage c:s value set value 5`, `... list append value {id:1}`, `... a.b[0].c set from entity @s Pos[1]`,
  `data modify entity @s CustomName set value {text:"Name"}`, `data merge storage c:s {a:1,b:[1,2,3],c:"str",d:1.5f}`,
  `data remove storage c:s value`, `data get entity @s SelectedItem`,
  `data modify entity @s equipment.mainhand set value {id:"minecraft:stick",count:1}`.
- 26.3 adds a `compute` source: `data modify storage c:s v set compute default integer <provider>`.

## Items: give / item / clear / loot  (see item-components.md)
- OK: `give @s minecraft:diamond 64`, `give @s diamond`, `give @s minecraft:diamond_sword[damage=5,unbreakable={}]`.
- BAD: `give @s minecraft:diamond_sword{Damage:5}` (`Expected whitespace to end one argument`).
- OK: `item replace entity @s weapon.mainhand with minecraft:stick`, `... armor.head with minecraft:diamond_helmet 1`,
  `... armor.body with minecraft:diamond_horse_armor`, `... hotbar.0 ...`, `... mob.inventory.0 ...`,
  `item replace block ~ ~ ~ container.0 with minecraft:stone`, `item modify entity @s weapon.mainhand c:my_modifier`,
  `item fill entity @s container.* with minecraft:stone` (26.3), `clear @s *[custom_data~{c:{wand:1b}}]`.
- BAD slot `villager.0` (`Can't find element 'minecraft:villager.0' in registry 'minecraft:slot_source'`): renamed to
  `mob.inventory.N` in 26.1. Slot arguments are now **slot sources**: a slot name/pattern or an ID from `slot_source/`.
- `item` subcommands: replace, modify, fill (26.3), override (26.3). `/loot give|spawn|insert|replace ... loot <table>`.

## Entities
- OK: `summon minecraft:zombie ~ ~ ~ {NoAI:1b,Tags:["c.z"],CustomName:{text:"Bob"}}`,
  `summon minecraft:item ~ ~ ~ {Item:{id:"minecraft:diamond",count:1}}`,
  `summon minecraft:armor_stand ~ ~ ~ {equipment:{head:{id:"minecraft:diamond_helmet",count:1}}}`,
  `summon minecraft:text_display ~ ~ ~ {text:{text:"Hi",color:"gold"},billboard:"center"}`.
- Integer x in summon positions is block-centred: `summon minecraft:marker 0 -60 0` -> Pos x = 0.5 (runtime-verified for x; z presumably the same, y not checked).
- BAD: `summon minecraft:zombie ~ ^ ~` (`Cannot mix world and local coordinates`), `tp @s @e[type=minecraft:pig]`
  (destination must be one entity).
- `tp`/`teleport`, `kill`, `ride @s mount <single>`, `ride @s dismount`, `rotate @s 90 0`, `rotate @s facing entity @p`,
  `damage @s 5 minecraft:magic`, `damage @s 2 minecraft:arrow by @p` all OK.

## Blocks
- OK: `setblock ~ ~ ~ minecraft:chest[facing=east]{Items:[]} replace`, `fill ~-1 ~ ~-1 ~1 ~ ~1 minecraft:air replace minecraft:stone`,
  `fill ... minecraft:glass hollow`, `clone 0 0 0 1 1 1 5 5 5 masked`. `place feature minecraft:oak ~ ~ ~`.
- BAD: `setblock 0 0 0.5 ...` (`Invalid integer`), unknown block, invalid property value
  (`Block minecraft:oak_stairs does not accept 'up' for facing property`).

## Effects, attributes, enchant
- OK: `effect give @s minecraft:speed 30 1 true`, `effect give @s minecraft:speed infinite 0`, `effect clear @s`,
  `enchant @s minecraft:sharpness 2`, `attribute @s minecraft:max_health base set 40`,
  `attribute @s minecraft:movement_speed modifier add c:fast 0.1 add_multiplied_base`, `attribute @s minecraft:scale base get`.
- BAD: `attribute @s minecraft:generic.max_health ...` (prefix removed in 1.21.2), `effect give @s minecraft:speedy 10`.

## Particles and sounds
- OK: `particle minecraft:flame ~ ~1 ~ 0.1 0.1 0.1 0.01 10 force`,
  `particle minecraft:dust{color:[1.0,0.0,0.0],scale:1.0} ~ ~1 ~ 0 0 0 0 1`.
- BAD: `particle minecraft:dust 1.0 0.0 0.0 1.0 ~ ~ ~` (old positional options: `No key scale`).
- OK: `playsound minecraft:entity.experience_orb.pickup master @a ~ ~ ~ 1 1`, `stopsound @a master`.

## Text output (see text-components.md)
- OK: `tellraw @a {text:"snbt",color:"red"}`, `tellraw @a {"text":"json","color":"red"}`, `tellraw @a "plain"`,
  `title @a title {text:"Title"}`, `title @a times 10 70 20`, `title @a actionbar "bar"`.

## Other verified OK
`bossbar add c:bar {text:"Boss"}`, `bossbar set c:bar max 100|players @a|color red`, `team add c.red`,
`team modify c.red color red`, `team join c.red @s`, `tag @s add|remove c.t`, `random value 1..6`, `random roll 1..100`,
`time set day|noon`, `time add 100`, `time query gametime`, `time of minecraft:overworld set minecraft:day`,
`time of minecraft:overworld query time`, `weather clear`, `difficulty peaceful`, `forceload add 0 0`,
`spreadplayers 0 0 5 20 false @a`, `advancement grant @s only minecraft:story/root`, `recipe give @s minecraft:diamond_sword`,
`experience add @s 10 levels`, `xp set @s 0 points`, `spawnpoint @s ~ ~ ~`, `setworldspawn 0 64 0`, `worldborder set 100`,
`locate structure minecraft:village_plains`, `locate biome minecraft:plains`, `trigger c.trig set 1`, `msg @a hello`,
`me waves`, `reload`, `datapack list`, `stopwatch create c:sw`, `stopwatch query c:sw 20`,
`swing @s mainhand stab 10t`, `swing @s offhand whack`, `dialog show @a minecraft:server_links`, `waypoint list`,
`fetchprofile name Notch`, `posteffect add @a minecraft:invert`.

## New in 26.x (syntax from commands.json)
- `compute default|block <pos>|entity <single> float <context_float_provider> [<scale>]` or `... integer <context_int_provider>`.
  Provider = an ID of a `context_*_provider` file **or** an inline SNBT object. Verified OK:
  `compute default integer {type:"minecraft:uniform",min:1,max:6}`,
  `compute default float {type:"minecraft:uniform",min:0.0,max:1.0} 100`,
  `compute entity @s float {type:"minecraft:storage",storage:"c:s",path:"v"}`,
  `execute store result score #r c.obj run compute default integer {type:"minecraft:uniform",min:1,max:6}`.
  BAD: a bare number `compute default integer 5` (parsed as ID `minecraft:5`); `{type:"minecraft:sum",...}`
  (renamed `add`); `{type:"minecraft:add",left:1,right:2}` (`No key inputs`: `add` takes `inputs`).
- `swing [<targets>] [mainhand|offhand] [whack|stab|none] [<duration>]` (BAD animation `bonk`).
- `stopwatch create|query <id> [scale]|restart|remove <id>`; `execute if stopwatch <id> <range>`.
- `posteffect add|remove <players> <id>`, `posteffect clear <players>`, `posteffect list <player>`.
- `item fill|override`, `execute if|unless slots (block <pos>|entity <targets>) <slot_source>`.
- `time of <world_clock> set|add|pause|resume|rate|query ...` (26.1 world clocks).
- `tick` exists but needs permission level 3: not usable from functions.

## Combat, attributes, scoreboard display (probe 2026-10-10, `knowledge/_research/probes/probe-tmg-1.txt`, `-2.txt`)
- [V] `attribute <single target> <attr> modifier add <id> <value> add_value|add_multiplied_base|add_multiplied_total`,
  `... modifier remove <id>`, `... get`, `... base get`. Target is single: use `execute as ... run attribute @s ...`.
  `movement_speed modifier add x -1 add_multiplied_total` -> `get` prints `is 0.0`; remove -> back to base (armor stand 0.7).
  Armor stands have `movement_speed` 0.7, `jump_strength` 0.42, `entity_interaction_range` 3.0, `max_health` 20.
- [V] `max_health modifier add ... 20 add_value` does not heal; `effect give <e> minecraft:instant_health 1 5 true`
  heals to the new max next tick (pig 9 -> 30, armor stand -> 30). Removing the modifier clamps Health to the new max.
- [V] `execute on attacker` = the entity that last damaged @s (works after `damage <t> 1 minecraft:mob_attack by <e>`);
  gone again ~100 ticks later (checked at 110). `HurtTime` is `10s` right after a hit and still 10 when the next tick's
  `#minecraft:tick` function runs (functions run before entity ticks; probe pack logged it), then 9, ..., 0.
- [V] Armor stands ignore `minecraft:mob_attack` (`Target is invulnerable to the given damage type`): use `NoAI` pigs as
  damage stand-ins. Team `friendlyFire false` does NOT stop `damage ... by <mob teammate>` (mobs); player behaviour unverified.
- [V] `execute if block ~ ~ ~ minecraft:lava` detects an entity standing in lava. There is no `#minecraft:lava` block tag.
- [V] Entity predicate `{"type":"minecraft:entity_properties","entity":"this","predicate":{"minecraft:flags":{"is_on_fire":true}}}`
  works as `@s[predicate=ns:on_fire]` and `execute if predicate ns:on_fire` (true after `data merge entity @s {Fire:100s}`).
- [V] `execute if dimension <custom ns:dim>` / `unless dimension` work with a pack dimension.
- [V] `scoreboard objectives setdisplay list <obj>` (tab list); `scoreboard players display numberformat <holder> <obj> fixed
  {text:"$7.50"}` and `scoreboard objectives modify <obj> numberformat styled {color:"gold"}` are accepted. Client rendering unverified.
- [V] A macro argument may contain `$`: `$say $(sym)$(d).$(pad)$(c)` with `{sym:"$",d:7,pad:"0",c:5}` prints `$7.05`.
- [V] `execute store result score #t o run time query gametime` stores the game time (ticks).
- [V] Game rules `immediate_respawn` (default false) and `pvp` (default true) exist in 26.3 (`registries.json minecraft:game_rule`).
- [V] Criteria `minecraft.custom:minecraft.leave_game` and `trigger` objectives create fine.

## Shrinking circle and empty function tags (probe 2026-10-10, `knowledge/_research/probes/probe-tmg-3.txt`, pack `tmg-zone-pack`)
- [V] A function tag file `{"values":[]}` loads without error and `function #ns:empty` runs (does nothing).
- [V] Score-only circle sweep: rows/cells by recursion with `execute ... positioned ~1 ~ ~` / `~ ~ ~1`, d2 = dx*dx+dz*dz
  via `scoreboard players operation`, `setblock` when `r2 < d2 <= Rb2`. R=4, r2=4 on a 9x9 stone square changed
  exactly 36 cells (lava or air); 45 stayed stone. Only one macro call per sweep (`positioned ~-$(R) ~ ~-$(R)`).
- [V] `setblock ... minecraft:lava` in the top layer of a 2-layer floor does not spread: after 60 ticks no lava above
  or below. (A 1-layer floor would let lava fall into the void: keep a solid layer under any lava.)
- [V] Items: copper armor (`copper_helmet/chestplate/leggings/boots`) and `copper_sword` exist. Armor points per full
  set (reports): leather 7, copper 10, golden 11, chainmail 12, iron 15, diamond 20 (+8 toughness), netherite 20 (+12).
  Sword attack_damage: wooden/golden 3, stone/copper 4, iron 5, diamond 6, netherite 7.
