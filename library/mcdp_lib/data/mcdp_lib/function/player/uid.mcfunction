#> mcdp_lib:player/uid
#> Purpose: Unique, stable integer id for @s (assigned on first call; works for any entity).
#> Inputs: none
#> Outputs: score @s mcdp_lib.id; return the id
#> Effects: may assign the id
#> Context: as an entity (@s)
#> Cost: fast (no macro)
#> Example: execute as @a run function mcdp_lib:player/uid
execute if score @s mcdp_lib.id matches 1.. run return run scoreboard players get @s mcdp_lib.id
scoreboard players add #next mcdp_lib.id 1
scoreboard players operation @s mcdp_lib.id = #next mcdp_lib.id
return run scoreboard players get @s mcdp_lib.id
