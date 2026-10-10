#> slice:round/time_up - timer callback (rules.time_limit_seconds elapsed)
execute if score #state slice.round matches 2 run function slice:round/end
