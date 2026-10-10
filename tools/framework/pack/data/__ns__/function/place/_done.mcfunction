#> __ns__:place/_done - internal: all tiles placed; continue with the round (state 1) or go idle after a restore (4)
execute if score #state __ns__.round matches 1 run return run function __ns__:round/begin
execute if score #state __ns__.round matches 4 run scoreboard players set #state __ns__.round 0
