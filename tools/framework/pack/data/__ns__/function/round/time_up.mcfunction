#> __ns__:round/time_up - timer callback (rules.time_limit_seconds elapsed). rules.time_up "end" (default) ends
#> the round; "hook" runs the minigame's time_up hook instead and the round keeps running (e.g. a shrinking zone).
execute unless score #state __ns__.round matches 2 run return fail
execute if data storage __ns__:round current.rules{time_up:"hook"} run return run function __ns__:round/hook {hook:"time_up"}
function __ns__:round/end
