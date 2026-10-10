#> __ns__:round/abort - stop the current round without winners or payout (admin); restores everything
execute if score #state __ns__.round matches 0 run return fail
execute if score #state __ns__.round matches 4 run return fail
function __lib__:timer/stop_global {name:"__ns__.rtimer"}
execute if score #state __ns__.round matches 1 run return run function __ns__:round/_abort_placing
scoreboard players set #state __ns__.round 3
function __ns__:round/teardown
return 1
