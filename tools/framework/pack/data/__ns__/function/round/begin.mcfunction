#> __ns__:round/begin - internal: the map is placed; save participants, apply rules, teleport, start the timer
function __ns__:round/_mark_placed with storage __ns__:round current.map
scoreboard players set #state __ns__.round 2
execute as @e[tag=__ns__.in_round] run function __lib__:player/save_position
execute as @a[tag=__ns__.in_round] run function __lib__:player/save_gamemode
execute as @a[tag=__ns__.in_round] run function __lib__:player/save_inventory
execute if data storage __ns__:round current.rules{clear_inventory:1b} run clear @a[tag=__ns__.in_round]
data modify storage __lib__:in rules set from storage __ns__:round current.rules_lib
function __lib__:rules/apply {targets:"@e[tag=__ns__.in_round]"}
data modify storage __ns__:round spawns set from storage __ns__:round current.map.spawns
function __lib__:random/shuffle {storage:"__ns__:round",path:"spawns"}
execute as @e[tag=__ns__.in_round] run function __ns__:round/_spawn_one
execute unless data storage __ns__:round current.rules{time_limit_seconds:0} run function __ns__:round/_start_timer
tellraw @a[tag=__ns__.in_round] [{text:"Now playing ",color:"gold"},{storage:"__ns__:round",nbt:"current.game.name",color:"yellow"},{text:" on "},{storage:"__ns__:round",nbt:"current.map.name",color:"yellow"}]
function __ns__:round/hook {hook:"start"}
execute as @e[tag=__ns__.in_round] at @s run function __ns__:round/hook {hook:"player_start"}
return 1
