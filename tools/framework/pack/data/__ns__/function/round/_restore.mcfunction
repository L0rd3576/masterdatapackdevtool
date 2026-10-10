#> __ns__:round/_restore - internal: re-place the map's tiles over the next ticks (state 4), then go idle
scoreboard players set #state __ns__.round 4
function __ns__:place/start
return 1
