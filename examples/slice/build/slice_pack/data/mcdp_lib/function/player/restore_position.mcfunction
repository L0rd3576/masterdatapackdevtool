#> mcdp_lib:player/restore_position
#> Purpose: Teleport @s back to the position saved by save_position (custom dimensions restore only for players).
#> Inputs: none
#> Outputs: return 1, or fail if nothing was saved
#> Effects: teleports @s
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @a run function mcdp_lib:player/restore_position
function mcdp_lib:_internal/player/peek
execute unless data storage mcdp_lib:internal cur.pos run return fail
data modify storage mcdp_lib:internal tp set value {}
data modify storage mcdp_lib:internal tp.dim set from storage mcdp_lib:internal cur.dim
data modify storage mcdp_lib:internal tp.x set from storage mcdp_lib:internal cur.pos[0]
data modify storage mcdp_lib:internal tp.y set from storage mcdp_lib:internal cur.pos[1]
data modify storage mcdp_lib:internal tp.z set from storage mcdp_lib:internal cur.pos[2]
data modify storage mcdp_lib:internal tp.yaw set from storage mcdp_lib:internal cur.rot[0]
data modify storage mcdp_lib:internal tp.pitch set from storage mcdp_lib:internal cur.rot[1]
function mcdp_lib:_internal/player/tp with storage mcdp_lib:internal tp
return 1
