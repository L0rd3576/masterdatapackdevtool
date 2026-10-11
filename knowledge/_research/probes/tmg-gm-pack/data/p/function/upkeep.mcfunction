execute as @e[type=minecraft:armor_stand,tag=g] run function p:gm_check
execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{tmg_gm:{}}] run kill @s
