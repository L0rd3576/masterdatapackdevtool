#> mcdp_lib:player/restore_inventory
#> Purpose: Replace @s's items with the ones saved by save_inventory (exact components kept).
#> Inputs: none
#> Outputs: return 1, or fail if nothing was saved
#> Effects: clears then refills @s's inventory/equipment; summons and removes a temporary item_display
#> Context: as an entity (@s)
#> Cost: macro; one call per item
#> Example: execute as @a at @s run function mcdp_lib:player/restore_inventory
function mcdp_lib:_internal/player/peek
execute unless data storage mcdp_lib:internal cur.eq run return fail
execute if entity @s[type=minecraft:player] run clear @s
item replace entity @s armor.head with minecraft:air
item replace entity @s armor.chest with minecraft:air
item replace entity @s armor.legs with minecraft:air
item replace entity @s armor.feet with minecraft:air
item replace entity @s armor.body with minecraft:air
item replace entity @s weapon.mainhand with minecraft:air
item replace entity @s weapon.offhand with minecraft:air
item replace entity @s saddle with minecraft:air
summon minecraft:item_display ~ ~ ~ {Tags:["mcdp_lib.scratch"]}
execute if data storage mcdp_lib:internal cur.eq.head run function mcdp_lib:_internal/player/put_eq {key:"head",slot:"armor.head"}
execute if data storage mcdp_lib:internal cur.eq.chest run function mcdp_lib:_internal/player/put_eq {key:"chest",slot:"armor.chest"}
execute if data storage mcdp_lib:internal cur.eq.legs run function mcdp_lib:_internal/player/put_eq {key:"legs",slot:"armor.legs"}
execute if data storage mcdp_lib:internal cur.eq.feet run function mcdp_lib:_internal/player/put_eq {key:"feet",slot:"armor.feet"}
execute if data storage mcdp_lib:internal cur.eq.body run function mcdp_lib:_internal/player/put_eq {key:"body",slot:"armor.body"}
execute if data storage mcdp_lib:internal cur.eq.mainhand run function mcdp_lib:_internal/player/put_eq {key:"mainhand",slot:"weapon.mainhand"}
execute if data storage mcdp_lib:internal cur.eq.offhand run function mcdp_lib:_internal/player/put_eq {key:"offhand",slot:"weapon.offhand"}
execute if data storage mcdp_lib:internal cur.eq.saddle run function mcdp_lib:_internal/player/put_eq {key:"saddle",slot:"saddle"}
data modify storage mcdp_lib:internal ri set from storage mcdp_lib:internal cur.inv
function mcdp_lib:_internal/player/inv_step
kill @e[type=minecraft:item_display,tag=mcdp_lib.scratch]
return 1
