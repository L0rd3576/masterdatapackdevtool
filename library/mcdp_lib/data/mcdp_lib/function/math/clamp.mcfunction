#> mcdp_lib:math/clamp
#> Purpose: Clamp #value to [#min, #max] without macros (hot-path safe).
#> Inputs: scores #value, #min, #max on mcdp_lib.in
#> Outputs: score #result mcdp_lib.out; return the result
#> Effects: none
#> Context: any
#> Cost: fast (scoreboard only)
#> Example: execute store result score @s my.mana run function mcdp_lib:math/clamp
scoreboard players operation #result mcdp_lib.out = #value mcdp_lib.in
scoreboard players operation #result mcdp_lib.out > #min mcdp_lib.in
scoreboard players operation #result mcdp_lib.out < #max mcdp_lib.in
return run scoreboard players get #result mcdp_lib.out
