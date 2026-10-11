#> __ns__:win/last_team/_mark - internal: as a source entity: tag it and every participant with its __ns__.tid winner
tag @s add __ns__.winner
scoreboard players reset #cur __ns__.var
scoreboard players operation #cur __ns__.var = @s __ns__.tid
execute as @e[tag=__ns__.in_round] if score @s __ns__.tid = #cur __ns__.var run tag @s add __ns__.winner
