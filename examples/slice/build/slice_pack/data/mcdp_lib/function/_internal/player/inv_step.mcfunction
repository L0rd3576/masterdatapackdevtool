# Restores player Inventory entries: Slot 0-8 -> hotbar.N, 9-35 -> inventory.N-9.
execute unless data storage mcdp_lib:internal ri[0] run return 0
execute store result score #s mcdp_lib.var run data get storage mcdp_lib:internal ri[0].Slot
data modify storage mcdp_lib:internal ri_args set value {prefix:"hotbar"}
execute if score #s mcdp_lib.var matches 9.. run data modify storage mcdp_lib:internal ri_args.prefix set value "inventory"
execute if score #s mcdp_lib.var matches 9.. run scoreboard players remove #s mcdp_lib.var 9
execute store result storage mcdp_lib:internal ri_args.n int 1 run scoreboard players get #s mcdp_lib.var
data modify storage mcdp_lib:internal ri_item set from storage mcdp_lib:internal ri[0]
data remove storage mcdp_lib:internal ri_item.Slot
data modify entity @n[type=minecraft:item_display,tag=mcdp_lib.scratch] item set from storage mcdp_lib:internal ri_item
execute if score #s mcdp_lib.var matches 0..26 run function mcdp_lib:_internal/player/put_inv with storage mcdp_lib:internal ri_args
data remove storage mcdp_lib:internal ri[0]
function mcdp_lib:_internal/player/inv_step
