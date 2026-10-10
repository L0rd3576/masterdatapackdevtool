#> slice:round/_clear_items {x,y,z,dx,dy,dz,dimension} - internal: remove dropped items/xp inside the map box
$execute in $(dimension) positioned $(x) $(y) $(z) run kill @e[type=minecraft:item,dx=$(dx),dy=$(dy),dz=$(dz)]
$execute in $(dimension) positioned $(x) $(y) $(z) run kill @e[type=minecraft:experience_orb,dx=$(dx),dy=$(dy),dz=$(dz)]
