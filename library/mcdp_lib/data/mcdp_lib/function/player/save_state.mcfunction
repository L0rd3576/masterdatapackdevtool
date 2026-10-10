#> mcdp_lib:player/save_state
#> Purpose: save_position + save_gamemode + save_inventory in one call.
#> Inputs: none
#> Outputs: return 1
#> Effects: writes storage mcdp_lib:internal saved
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @a run function mcdp_lib:player/save_state
function mcdp_lib:player/save_position
function mcdp_lib:player/save_gamemode
function mcdp_lib:player/save_inventory
return 1
