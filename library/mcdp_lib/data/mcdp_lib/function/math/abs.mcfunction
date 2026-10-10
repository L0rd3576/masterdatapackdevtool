#> mcdp_lib:math/abs
#> Purpose: Absolute value of #value.
#> Inputs: score #value mcdp_lib.in
#> Outputs: score #result mcdp_lib.out; return the result
#> Effects: none
#> Context: any
#> Cost: fast (scoreboard only)
#> Example: function mcdp_lib:math/abs
scoreboard players operation #result mcdp_lib.out = #value mcdp_lib.in
execute if score #result mcdp_lib.out matches ..-1 run scoreboard players operation #result mcdp_lib.out *= #neg1 mcdp_lib.var
return run scoreboard players get #result mcdp_lib.out
