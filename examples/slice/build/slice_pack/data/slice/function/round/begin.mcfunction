#> slice:round/begin - internal: the map is placed; save participants, apply rules, teleport, start the timer
function slice:round/_mark_placed with storage slice:round current.map
scoreboard players set #state slice.round 2
execute as @e[tag=slice.in_round] run function mcdp_lib:player/save_position
execute as @a[tag=slice.in_round] run function mcdp_lib:player/save_gamemode
execute as @a[tag=slice.in_round] run function mcdp_lib:player/save_inventory
execute if data storage slice:round current.rules{clear_inventory:1b} run clear @a[tag=slice.in_round]
data modify storage mcdp_lib:in rules set from storage slice:round current.rules_lib
function mcdp_lib:rules/apply {targets:"@e[tag=slice.in_round]"}
data modify storage slice:round spawns set from storage slice:round current.map.spawns
function mcdp_lib:random/shuffle {storage:"slice:round",path:"spawns"}
execute as @e[tag=slice.in_round] run function slice:round/_spawn_one
execute unless data storage slice:round current.rules{time_limit_seconds:0} run function slice:round/_start_timer
tellraw @a[tag=slice.in_round] [{text:"Now playing ",color:"gold"},{storage:"slice:round",nbt:"current.game.name",color:"yellow"},{text:" on "},{storage:"slice:round",nbt:"current.map.name",color:"yellow"}]
function slice:round/hook {hook:"start"}
execute as @e[tag=slice.in_round] at @s run function slice:round/hook {hook:"player_start"}
return 1
