#> mcdp_lib:math/div
#> Purpose: Safe floor division #a / #b (rounds toward -infinity like the scoreboard: -7/2 = -4).
#> Inputs: scores #a, #b on mcdp_lib.in
#> Outputs: score #result mcdp_lib.out (0 if #b is 0); return the result, or fail when #b is 0
#> Effects: none
#> Context: any
#> Cost: fast (scoreboard only)
#> Example: execute store success score #ok my.v run function mcdp_lib:math/div
scoreboard players set #result mcdp_lib.out 0
execute if score #b mcdp_lib.in matches 0 run return fail
scoreboard players operation #result mcdp_lib.out = #a mcdp_lib.in
scoreboard players operation #result mcdp_lib.out /= #b mcdp_lib.in
return run scoreboard players get #result mcdp_lib.out
