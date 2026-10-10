#> mcdp_lib:random/int
#> Purpose: Uniform random integer in [min, max] (inclusive).
#> Inputs: macro {min:int, max:int}
#> Outputs: score #result mcdp_lib.out; return the number, or fail if max < min
#> Effects: none
#> Context: any
#> Cost: macro; scoreboard-only version: mcdp_lib:random/int_fast
#> Example: execute store result score @s my.roll run function mcdp_lib:random/int {min:1,max:6}
# Not `random value $(min)..$(max)`: that errors when min = max ("range ... must be at least 1").
$scoreboard players set #lo mcdp_lib.var $(min)
$scoreboard players set #bound mcdp_lib.var $(max)
scoreboard players operation #bound mcdp_lib.var -= #lo mcdp_lib.var
scoreboard players add #bound mcdp_lib.var 1
execute if score #bound mcdp_lib.var matches ..0 run return fail
function mcdp_lib:_internal/random/below
scoreboard players operation #result mcdp_lib.out = #r mcdp_lib.var
scoreboard players operation #result mcdp_lib.out += #lo mcdp_lib.var
return run scoreboard players get #result mcdp_lib.out
