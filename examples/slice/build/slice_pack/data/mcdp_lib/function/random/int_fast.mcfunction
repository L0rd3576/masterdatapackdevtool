#> mcdp_lib:random/int_fast
#> Purpose: Random integer in [#min, #max] without macros (modulo of a 31-bit roll; bias is negligible).
#> Inputs: scores #min, #max on mcdp_lib.in (#min <= #max)
#> Outputs: score #result mcdp_lib.out; return the number, or fail if #max < #min
#> Effects: none
#> Context: any
#> Cost: fast (scoreboard only)
#> Example: scoreboard players set #min mcdp_lib.in 1
scoreboard players operation #bound mcdp_lib.var = #max mcdp_lib.in
scoreboard players operation #bound mcdp_lib.var -= #min mcdp_lib.in
scoreboard players add #bound mcdp_lib.var 1
execute if score #bound mcdp_lib.var matches ..0 run return fail
function mcdp_lib:_internal/random/below
scoreboard players operation #result mcdp_lib.out = #r mcdp_lib.var
scoreboard players operation #result mcdp_lib.out += #min mcdp_lib.in
return run scoreboard players get #result mcdp_lib.out
