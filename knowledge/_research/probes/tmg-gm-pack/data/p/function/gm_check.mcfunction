execute store result score @s p.c if items entity @s weapon.* *[minecraft:custom_data~{tmg_gm:{}}]
execute unless items entity @s weapon.mainhand *[minecraft:custom_data~{tmg_gm:{key:"start"}}] run scoreboard players add #miss p.c 1
