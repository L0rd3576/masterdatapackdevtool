scoreboard players add #p mf 1
function mf:plain_body
execute if score #p mf < #lim mf run function mf:perf_plain
