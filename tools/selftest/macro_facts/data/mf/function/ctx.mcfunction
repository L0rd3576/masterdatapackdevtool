tag @s add mf.ran
execute store result score #ctx_y mf run data get entity @s Pos[1]
summon minecraft:marker ~ ~ ~ {Tags:["mf.here"]}
