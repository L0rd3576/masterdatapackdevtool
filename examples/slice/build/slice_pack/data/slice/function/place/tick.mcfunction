#> slice:place/tick - internal: place up to #tiles_per_tick queued tiles, then continue the round state
scoreboard players operation #k slice.var = #tiles_per_tick slice.cfg
function slice:place/_step
execute unless data storage slice:build queue[0] run function slice:place/_done
