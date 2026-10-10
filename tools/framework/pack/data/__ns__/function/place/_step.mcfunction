#> __ns__:place/_step - internal: place one tile in the arena dimension, repeat while #k > 0
execute unless data storage __ns__:build queue[0] run return 0
execute in __ns__:__arena__ run function __ns__:place/_tile with storage __ns__:build queue[0]
data remove storage __ns__:build queue[0]
scoreboard players remove #k __ns__.var 1
execute if score #k __ns__.var matches 1.. run function __ns__:place/_step
