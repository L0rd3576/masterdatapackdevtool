execute unless data storage mcdp_lib:internal f.list[0] run return -1
data modify storage mcdp_lib:internal f.cur set from storage mcdp_lib:internal f.list[0]
execute store success score #diff mcdp_lib.var run data modify storage mcdp_lib:internal f.cur set from storage mcdp_lib:in value
execute if score #diff mcdp_lib.var matches 0 run return run scoreboard players get #idx mcdp_lib.var
data remove storage mcdp_lib:internal f.list[0]
scoreboard players add #idx mcdp_lib.var 1
return run function mcdp_lib:_internal/list/find_step
