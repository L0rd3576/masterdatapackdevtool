#> mcdp_lib:player/forget
#> Purpose: Delete everything saved for @s by the save_* functions.
#> Inputs: none
#> Outputs: return 1
#> Effects: removes @s's entry from storage mcdp_lib:internal saved
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @a run function mcdp_lib:player/forget
function mcdp_lib:_internal/player/open
return 1
