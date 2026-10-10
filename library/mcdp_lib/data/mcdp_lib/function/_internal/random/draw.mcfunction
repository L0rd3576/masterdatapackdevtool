# Moves a random element of sh.src to sh.dst while #n (remaining) > 0 and #k (wanted) > 0.
execute if score #n mcdp_lib.var matches ..0 run return 0
execute if score #k mcdp_lib.var matches ..0 run return 0
scoreboard players operation #bound mcdp_lib.var = #n mcdp_lib.var
function mcdp_lib:_internal/random/below
execute store result storage mcdp_lib:internal sh_args.i int 1 run scoreboard players get #r mcdp_lib.var
function mcdp_lib:_internal/random/move with storage mcdp_lib:internal sh_args
scoreboard players remove #n mcdp_lib.var 1
scoreboard players remove #k mcdp_lib.var 1
function mcdp_lib:_internal/random/draw
