#> slice:place/start - internal: queue the current map's structure tiles; place/tick places
#> #tiles_per_tick slice.cfg of them per game tick (budget from tools/mapgen/config.json placement)
data modify storage slice:build queue set from storage slice:round current.map.tiles
