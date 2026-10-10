#> slice:round/eliminate - as a participant: out for the rest of the round (players become spectators)
execute unless entity @s[tag=slice.alive] run return fail
tag @s remove slice.alive
gamemode spectator @s[type=minecraft:player]
function slice:round/hook {hook:"eliminated"}
return 1
