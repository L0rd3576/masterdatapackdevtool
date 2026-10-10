#> slice:round/abort - stop the current round without winners or payout (admin); restores everything
execute if score #state slice.round matches 0 run return fail
execute if score #state slice.round matches 4 run return fail
function mcdp_lib:timer/stop_global {name:"slice.rtimer"}
execute if score #state slice.round matches 1 run return run function slice:round/_abort_placing
scoreboard players set #state slice.round 3
function slice:round/teardown
return 1
