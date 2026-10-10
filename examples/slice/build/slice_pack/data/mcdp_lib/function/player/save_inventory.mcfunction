#> mcdp_lib:player/save_inventory
#> Purpose: Remember @s's items: player Inventory (slots 0-35) and equipment (armor, hands, body, saddle).
#> Inputs: none
#> Outputs: return 1
#> Effects: writes storage mcdp_lib:internal saved (does not clear the inventory)
#> Context: as an entity (@s); mobs/armor stands save equipment only
#> Cost: macro (UUID lookup)
#> Example: execute as @a run function mcdp_lib:player/save_inventory
function mcdp_lib:_internal/player/open
data modify storage mcdp_lib:internal cur.inv set value []
data modify storage mcdp_lib:internal cur.inv set from entity @s Inventory
data modify storage mcdp_lib:internal cur.eq set value {}
data modify storage mcdp_lib:internal cur.eq set from entity @s equipment
function mcdp_lib:_internal/player/close
return 1
