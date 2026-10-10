#> __ns__:tick - round state machine. #state: 0 idle, 1 placing map, 2 running, 3 ending, 4 restoring map
execute if score #state __ns__.round matches 1 run function __ns__:place/tick
execute if score #state __ns__.round matches 4 run function __ns__:place/tick
execute if score #state __ns__.round matches 2 run function __ns__:round/tick
execute if score #state __ns__.round matches 3 run function __ns__:round/_end_wait
