data modify storage mcdp_lib:internal fj set from storage mcdp_lib:internal fill_jobs[0]
execute store result score #y mcdp_lib.var run data get storage mcdp_lib:internal fj.y1
execute store result score #top mcdp_lib.var run data get storage mcdp_lib:internal fj.y2
execute store result score #e mcdp_lib.var run data get storage mcdp_lib:internal fj.layers
scoreboard players operation #e mcdp_lib.var > #1 mcdp_lib.var
scoreboard players operation #e mcdp_lib.var += #y mcdp_lib.var
scoreboard players remove #e mcdp_lib.var 1
scoreboard players operation #e mcdp_lib.var < #top mcdp_lib.var
execute store result storage mcdp_lib:internal fj.ye int 1 run scoreboard players get #e mcdp_lib.var
function mcdp_lib:_internal/world/fill_slab with storage mcdp_lib:internal fj
scoreboard players add #e mcdp_lib.var 1
execute store result storage mcdp_lib:internal fill_jobs[0].y1 int 1 run scoreboard players get #e mcdp_lib.var
execute if score #e mcdp_lib.var > #top mcdp_lib.var run function mcdp_lib:_internal/world/fill_done
