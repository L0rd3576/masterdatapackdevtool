#> mcdp_lib:item/kit
#> Purpose: Hand out a kit stored in mcdp_lib:config kits.<name>: entries {item,count} are given, entries {slot,item,count} replace that slot.
#> Inputs: macro {name:string}; storage mcdp_lib:config kits.<name> = [{item:"minecraft:iron_sword",count:1},{slot:"armor.head",item:"minecraft:iron_helmet",count:1}]
#> Outputs: return 1, or fail if the kit is missing/empty
#> Effects: gives/replaces items (give works on players only; slot entries work on any entity with the slot)
#> Context: as the receiver (@s)
#> Cost: macro; one call per entry
#> Example: execute as @a run function mcdp_lib:item/kit {name:"warrior"}
$execute unless data storage mcdp_lib:config kits.$(name)[0] run return fail
$data modify storage mcdp_lib:internal kit set from storage mcdp_lib:config kits.$(name)
function mcdp_lib:_internal/item/kit_step
return 1
