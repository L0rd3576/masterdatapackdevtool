#> slice:round/teardown - internal: undo rules, send participants back, clear drops, restore the map if needed
function mcdp_lib:rules/revert
execute as @a[tag=slice.in_round] run function mcdp_lib:player/restore_inventory
execute as @a[tag=slice.in_round] run function mcdp_lib:player/restore_gamemode
execute as @e[tag=slice.in_round] run function mcdp_lib:player/restore_position
scoreboard players reset @e[tag=slice.in_round] slice.score
tag @e remove slice.alive
tag @e remove slice.in_round
function slice:round/_clear_items with storage slice:round current.map.box
execute if data storage slice:round current.map{needs_restore:1b} run return run function slice:round/_restore
scoreboard players set #state slice.round 0
return 1
