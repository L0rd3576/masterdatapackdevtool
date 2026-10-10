#> __ns__:round/start - pick a random minigame/map/preset compatible with the queued participant count
#> (weights from pool.json, compiled per count into storage __ns__:registry by_count.n<count>) and start it.
#> Returns fail if a round is running or nothing fits.
execute unless score #state __ns__.round matches 0 run return fail
execute store result score #n __ns__.round if entity @e[tag=__ns__.queued]
execute store result storage __ns__:tmp sel.n int 1 run scoreboard players get #n __ns__.round
return run function __ns__:round/_pick with storage __ns__:tmp sel
