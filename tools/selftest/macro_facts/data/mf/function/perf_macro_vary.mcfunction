scoreboard players add #p mf 1
execute store result storage mf:o args.n int 1 run scoreboard players get #p mf
function mf:macro_body with storage mf:o args
execute if score #p mf < #lim mf run function mf:perf_macro_vary
