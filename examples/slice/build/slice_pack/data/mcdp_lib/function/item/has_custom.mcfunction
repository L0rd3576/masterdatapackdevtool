#> mcdp_lib:item/has_custom
#> Purpose: Count stacks in @s's slots that carry custom_data {mcdp_id:"<id>"}.
#> Inputs: macro {id:string, slots:string (slot or pattern, e.g. "weapon.mainhand", "container.*")}
#> Outputs: score #result mcdp_lib.out; return the number of matching stacks (0 = none)
#> Effects: none
#> Context: as an entity (@s)
#> Cost: macro; hot path: execute if items entity @s <slots> *[minecraft:custom_data~{mcdp_id:"<id>"}]
#> Example: execute as @a if function mcdp_lib:item/has_custom {id:"wand",slots:"weapon.mainhand"} run function my:cast
$execute store result score #result mcdp_lib.out if items entity @s $(slots) *[minecraft:custom_data~{mcdp_id:"$(id)"}]
return run scoreboard players get #result mcdp_lib.out
