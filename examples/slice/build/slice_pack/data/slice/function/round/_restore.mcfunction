#> slice:round/_restore - internal: re-place the map's tiles over the next ticks (state 4), then go idle
scoreboard players set #state slice.round 4
function slice:place/start
return 1
