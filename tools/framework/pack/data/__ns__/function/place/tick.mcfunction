#> __ns__:place/tick - internal: place up to #tiles_per_tick queued tiles, then continue the round state
scoreboard players operation #k __ns__.var = #tiles_per_tick __ns__.cfg
function __ns__:place/_step
execute unless data storage __ns__:build queue[0] run function __ns__:place/_done
