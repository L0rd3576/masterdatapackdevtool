#> mcdp_lib:math/mod
#> Purpose: Safe modulo #a % #b (sign follows #b: -7 % 2 = 1).
#> Inputs: scores #a, #b on mcdp_lib.in
#> Outputs: score #result mcdp_lib.out (0 if #b is 0); return the result, or fail when #b is 0
#> Effects: none
#> Context: any
#> Cost: fast (scoreboard only)
#> Example: function mcdp_lib:math/mod
scoreboard players set #result mcdp_lib.out 0
execute if score #b mcdp_lib.in matches 0 run return fail
scoreboard players operation #result mcdp_lib.out = #a mcdp_lib.in
scoreboard players operation #result mcdp_lib.out %= #b mcdp_lib.in
return run scoreboard players get #result mcdp_lib.out
