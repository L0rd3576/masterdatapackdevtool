execute unless data storage mcdp_lib:internal w.scan[0] run return 0
execute store result score #w mcdp_lib.var run data get storage mcdp_lib:internal w.scan[0].weight
scoreboard players operation #total mcdp_lib.var += #w mcdp_lib.var
data remove storage mcdp_lib:internal w.scan[0]
function mcdp_lib:_internal/random/w_sum
