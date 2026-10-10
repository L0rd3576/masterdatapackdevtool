#> __ns__:round/teardown - internal: undo rules, send participants back, clear drops, restore the map if needed
function __lib__:rules/revert
execute as @a[tag=__ns__.in_round] run function __lib__:player/restore_inventory
execute as @a[tag=__ns__.in_round] run function __lib__:player/restore_gamemode
execute as @e[tag=__ns__.in_round] run function __lib__:player/restore_position
scoreboard players reset @e[tag=__ns__.in_round] __ns__.score
tag @e remove __ns__.alive
tag @e remove __ns__.in_round
function __ns__:round/_clear_items with storage __ns__:round current.map.box
execute if data storage __ns__:round current.map{needs_restore:1b} run return run function __ns__:round/_restore
scoreboard players set #state __ns__.round 0
return 1
