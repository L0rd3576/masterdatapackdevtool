#> mcdp_lib:item/custom_to_slot
#> Purpose: Like item/custom but puts the item into a slot of @s (works on mobs and armor stands too).
#> Inputs: macro {slot:string, item:string, id:string, name:compound (text component), count:int}
#> Outputs: return 1
#> Effects: replaces the slot
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @p run function mcdp_lib:item/custom_to_slot {slot:"hotbar.0",item:"minecraft:stick",id:"wand",name:{text:"Wand"},count:1}
$item replace entity @s $(slot) with $(item)[minecraft:custom_name=$(name),minecraft:custom_data={mcdp_id:"$(id)"}] $(count)
return 1
