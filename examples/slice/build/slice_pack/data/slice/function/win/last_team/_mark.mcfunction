#> slice:win/last_team/_mark - internal: as a source entity: tag it and every participant with its slice.tid winner
tag @s add slice.winner
scoreboard players reset #cur slice.var
scoreboard players operation #cur slice.var = @s slice.tid
execute as @e[tag=slice.in_round] if score @s slice.tid = #cur slice.var run tag @s add slice.winner
