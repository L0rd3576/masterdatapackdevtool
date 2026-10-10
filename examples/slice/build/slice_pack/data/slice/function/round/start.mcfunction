#> slice:round/start - pick a random minigame/map/preset compatible with the queued participant count
#> (weights from pool.json, compiled per count into storage slice:registry by_count.n<count>) and start it.
#> Returns fail if a round is running or nothing fits.
execute unless score #state slice.round matches 0 run return fail
execute store result score #n slice.round if entity @e[tag=slice.queued]
execute store result storage slice:tmp sel.n int 1 run scoreboard players get #n slice.round
return run function slice:round/_pick with storage slice:tmp sel
