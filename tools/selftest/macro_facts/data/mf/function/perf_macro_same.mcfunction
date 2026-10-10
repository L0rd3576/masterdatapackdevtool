scoreboard players add #p mf 1
function mf:macro_body {n:1}
execute if score #p mf < #lim mf run function mf:perf_macro_same
