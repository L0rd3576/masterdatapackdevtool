#> block_brawl tick hook: score = wool mined this round (players; stand-ins in tests set __ns__.score directly)
execute as @a[tag=__ns__.alive] run scoreboard players operation @s __ns__.score = @s __ns__.bb_white
execute as @a[tag=__ns__.alive] run scoreboard players operation @s __ns__.score += @s __ns__.bb_orange
