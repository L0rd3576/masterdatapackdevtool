#> __ns__:place/start - internal: queue the current map's structure tiles; place/tick places
#> #tiles_per_tick __ns__.cfg of them per game tick (budget from tools/mapgen/config.json placement)
data modify storage __ns__:build queue set from storage __ns__:round current.map.tiles
