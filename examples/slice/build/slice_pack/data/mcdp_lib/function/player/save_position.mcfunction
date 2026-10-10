#> mcdp_lib:player/save_position
#> Purpose: Remember @s's position, rotation and dimension (keyed by UUID; works for any entity).
#> Inputs: none
#> Outputs: return 1
#> Effects: writes storage mcdp_lib:internal saved
#> Context: as an entity (@s)
#> Cost: macro (UUID lookup)
#> Example: execute as @a run function mcdp_lib:player/save_position
function mcdp_lib:_internal/player/open
data modify storage mcdp_lib:internal cur.pos set from entity @s Pos
data modify storage mcdp_lib:internal cur.rot set from entity @s Rotation
data modify storage mcdp_lib:internal cur.dim set value "minecraft:overworld"
execute if dimension minecraft:the_nether run data modify storage mcdp_lib:internal cur.dim set value "minecraft:the_nether"
execute if dimension minecraft:the_end run data modify storage mcdp_lib:internal cur.dim set value "minecraft:the_end"
data modify storage mcdp_lib:internal cur.dim set from entity @s Dimension
function mcdp_lib:_internal/player/close
return 1
