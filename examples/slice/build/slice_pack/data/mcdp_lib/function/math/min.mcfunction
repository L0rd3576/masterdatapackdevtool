#> mcdp_lib:math/min
#> Purpose: Smaller of #a and #b.
#> Inputs: scores #a, #b on mcdp_lib.in
#> Outputs: score #result mcdp_lib.out; return the result
#> Effects: none
#> Context: any
#> Cost: fast (scoreboard only)
#> Example: execute store result score @s my.v run function mcdp_lib:math/min
scoreboard players operation #result mcdp_lib.out = #a mcdp_lib.in
scoreboard players operation #result mcdp_lib.out < #b mcdp_lib.in
return run scoreboard players get #result mcdp_lib.out
