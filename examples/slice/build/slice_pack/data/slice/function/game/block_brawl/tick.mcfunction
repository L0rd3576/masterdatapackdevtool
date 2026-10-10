#> block_brawl tick hook: score = wool mined this round (players; stand-ins in tests set slice.score directly)
execute as @a[tag=slice.alive] run scoreboard players operation @s slice.score = @s slice.bb_white
execute as @a[tag=slice.alive] run scoreboard players operation @s slice.score += @s slice.bb_orange
