#> slice:win/last_team/_take - internal: as an uncounted alive entity: remove it and every uncounted entity with
#> the same slice.tid from the set (an entity without a tid is a team of its own)
tag @s remove slice.unc
scoreboard players reset #cur slice.var
scoreboard players operation #cur slice.var = @s slice.tid
execute as @e[tag=slice.unc] if score @s slice.tid = #cur slice.var run tag @s remove slice.unc
