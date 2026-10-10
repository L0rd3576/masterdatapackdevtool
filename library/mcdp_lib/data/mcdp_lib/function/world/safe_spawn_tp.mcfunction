#> mcdp_lib:world/safe_spawn_tp
#> Purpose: Teleport @s on top of column (x, z) if that spot is safe (see world/safe_spawn).
#> Inputs: macro {x:int, z:int}
#> Outputs: return 1 if teleported, fail if unsafe
#> Effects: teleports @s
#> Context: as an entity (@s), in the target dimension
#> Cost: macro
#> Example: execute as @p run function mcdp_lib:world/safe_spawn_tp {x:100,z:-40}
$execute store success score #ok mcdp_lib.var run function mcdp_lib:world/safe_spawn {x:$(x),z:$(z)}
execute if score #ok mcdp_lib.var matches 0 run return fail
data modify storage mcdp_lib:internal tp set value {}
data modify storage mcdp_lib:internal tp.x set from storage mcdp_lib:out pos[0]
data modify storage mcdp_lib:internal tp.y set from storage mcdp_lib:out pos[1]
data modify storage mcdp_lib:internal tp.z set from storage mcdp_lib:out pos[2]
function mcdp_lib:_internal/world/tp_xyz with storage mcdp_lib:internal tp
return 1
