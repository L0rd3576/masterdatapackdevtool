#> mcdp_lib:flow/break
#> Purpose: Inside a flow/repeat callback: stop the innermost repeat after the current call.
#> Inputs: none
#> Outputs: return 1, or fail if no repeat is running
#> Effects: shortens the innermost loop
#> Context: inside a flow/repeat callback
#> Cost: fast (no macro)
#> Example: execute if score #found my.v matches 1 run function mcdp_lib:flow/break
execute unless data storage mcdp_lib:internal rep[-1] run return fail
execute store result score #b mcdp_lib.var run data get storage mcdp_lib:internal rep[-1].i
scoreboard players add #b mcdp_lib.var 1
execute store result storage mcdp_lib:internal rep[-1].n int 1 run scoreboard players get #b mcdp_lib.var
return 1
