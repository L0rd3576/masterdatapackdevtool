#> __ns__:round/eliminate - as a participant: out for the rest of the round (players become spectators)
execute unless entity @s[tag=__ns__.alive] run return fail
tag @s remove __ns__.alive
tag @s add __ns__.elim_now
gamemode spectator @s[type=minecraft:player]
function __ns__:round/hook {hook:"eliminated"}
return 1
