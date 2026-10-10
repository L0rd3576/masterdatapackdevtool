#> slice:tick - round state machine. #state: 0 idle, 1 placing map, 2 running, 3 ending, 4 restoring map
execute if score #state slice.round matches 1 run function slice:place/tick
execute if score #state slice.round matches 4 run function slice:place/tick
execute if score #state slice.round matches 2 run function slice:round/tick
execute if score #state slice.round matches 3 run function slice:round/_end_wait
