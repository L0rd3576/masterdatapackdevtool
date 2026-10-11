#> __ns__:win/last_team/_take - internal: as an uncounted alive entity: remove it and every uncounted entity with
#> the same __ns__.tid from the set (an entity without a tid is a team of its own)
tag @s remove __ns__.unc
scoreboard players reset #cur __ns__.var
scoreboard players operation #cur __ns__.var = @s __ns__.tid
execute as @e[tag=__ns__.unc] if score @s __ns__.tid = #cur __ns__.var run tag @s remove __ns__.unc
