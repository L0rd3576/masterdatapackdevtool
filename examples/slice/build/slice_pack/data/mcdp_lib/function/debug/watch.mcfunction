#> mcdp_lib:debug/watch
#> Purpose: Toggle chat logging for @s (adds or removes tag mcdp_lib.debug).
#> Inputs: none
#> Outputs: return 1 if now watching, 0 if not
#> Effects: toggles tag mcdp_lib.debug on @s
#> Context: as a player (@s)
#> Cost: fast (no macro)
#> Example: execute as @p run function mcdp_lib:debug/watch
execute if entity @s[tag=mcdp_lib.debug] run return run function mcdp_lib:_internal/debug/unwatch
tag @s add mcdp_lib.debug
return 1
