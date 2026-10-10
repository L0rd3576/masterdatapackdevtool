#> mcdp_lib:item/set_slot_from_storage
#> Purpose: Put the item compound in mcdp_lib:in item into a slot of @s, keeping every component exactly.
#> Inputs: macro {slot:string (slot, e.g. "armor.head", "hotbar.0")}; storage mcdp_lib:in item
#> Outputs: return 1, or fail if mcdp_lib:in item.id is missing
#> Effects: replaces the slot; uses a temporary item_display at the current position
#> Context: as an entity with that slot (@s)
#> Cost: macro
#> Example: execute as @p at @s run function mcdp_lib:item/set_slot_from_storage {slot:"weapon.offhand"}
execute unless data storage mcdp_lib:in item.id run return fail
summon minecraft:item_display ~ ~ ~ {Tags:["mcdp_lib.scratch"]}
data modify entity @n[type=minecraft:item_display,tag=mcdp_lib.scratch] item set from storage mcdp_lib:in item
$item replace entity @s $(slot) from entity @n[type=minecraft:item_display,tag=mcdp_lib.scratch] contents
kill @e[type=minecraft:item_display,tag=mcdp_lib.scratch]
return 1
