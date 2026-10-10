#> slice:place/_done - internal: all tiles placed; continue with the round (state 1) or go idle after a restore (4)
execute if score #state slice.round matches 1 run return run function slice:round/begin
execute if score #state slice.round matches 4 run scoreboard players set #state slice.round 0
