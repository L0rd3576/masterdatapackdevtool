execute store result score #i mcdp_lib.var run data get storage mcdp_lib:internal rep[-1].i
execute store result score #n mcdp_lib.var run data get storage mcdp_lib:internal rep[-1].n
execute if score #i mcdp_lib.var >= #n mcdp_lib.var run return 0
scoreboard players operation #index mcdp_lib.out = #i mcdp_lib.var
function mcdp_lib:_internal/call with storage mcdp_lib:internal rep[-1].args
execute store result score #i mcdp_lib.var run data get storage mcdp_lib:internal rep[-1].i
scoreboard players add #i mcdp_lib.var 1
execute store result storage mcdp_lib:internal rep[-1].i int 1 run scoreboard players get #i mcdp_lib.var
function mcdp_lib:_internal/flow/rep_step
