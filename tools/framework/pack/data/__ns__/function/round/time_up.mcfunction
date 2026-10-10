#> __ns__:round/time_up - timer callback (rules.time_limit_seconds elapsed)
execute if score #state __ns__.round matches 2 run function __ns__:round/end
