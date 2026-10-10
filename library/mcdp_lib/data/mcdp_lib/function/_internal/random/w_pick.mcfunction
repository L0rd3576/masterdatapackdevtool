execute unless data storage mcdp_lib:internal w.list[0] run return fail
execute store result score #w mcdp_lib.var run data get storage mcdp_lib:internal w.list[0].weight
execute if score #r mcdp_lib.var < #w mcdp_lib.var run return run function mcdp_lib:_internal/random/w_found
scoreboard players operation #r mcdp_lib.var -= #w mcdp_lib.var
data remove storage mcdp_lib:internal w.list[0]
scoreboard players add #idx mcdp_lib.var 1
return run function mcdp_lib:_internal/random/w_pick
