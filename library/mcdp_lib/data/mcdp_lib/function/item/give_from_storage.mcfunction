#> mcdp_lib:item/give_from_storage
#> Purpose: Drop the item compound in mcdp_lib:in item ({id,count,components}) at the current position with no pickup delay (a player there picks it up next tick).
#> Inputs: storage mcdp_lib:in item
#> Outputs: return 1, or fail if mcdp_lib:in item.id is missing
#> Effects: summons an item entity
#> Context: at the receiver: execute as <player> at @s run ...
#> Cost: fast (no macro)
#> Example: execute as @p at @s run function mcdp_lib:item/give_from_storage
execute unless data storage mcdp_lib:in item.id run return fail
summon minecraft:item ~ ~ ~ {Item:{id:"minecraft:stone",count:1},PickupDelay:0s,Tags:["mcdp_lib.new"]}
data modify entity @n[type=minecraft:item,tag=mcdp_lib.new] Item set from storage mcdp_lib:in item
tag @e[type=minecraft:item,tag=mcdp_lib.new] remove mcdp_lib.new
return 1
