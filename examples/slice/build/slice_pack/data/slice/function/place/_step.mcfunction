#> slice:place/_step - internal: place one tile in the arena dimension, repeat while #k > 0
execute unless data storage slice:build queue[0] run return 0
execute in slice:arena run function slice:place/_tile with storage slice:build queue[0]
data remove storage slice:build queue[0]
scoreboard players remove #k slice.var 1
execute if score #k slice.var matches 1.. run function slice:place/_step
