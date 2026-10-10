#> mcdp_lib:player/restore_state
#> Purpose: restore_inventory + restore_gamemode + restore_position in one call.
#> Inputs: none
#> Outputs: return 1, or fail if nothing was saved
#> Effects: see the three restore functions
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @a at @s run function mcdp_lib:player/restore_state
function mcdp_lib:_internal/player/peek
execute unless data storage mcdp_lib:internal cur.uuid run return fail
execute at @s run function mcdp_lib:player/restore_inventory
function mcdp_lib:player/restore_gamemode
function mcdp_lib:player/restore_position
return 1
