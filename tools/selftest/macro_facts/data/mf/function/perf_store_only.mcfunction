scoreboard players add #p mf 1
execute store result storage mf:o args.n int 1 run scoreboard players get #p mf
function mf:plain_body
execute if score #p mf < #lim mf run function mf:perf_store_only
