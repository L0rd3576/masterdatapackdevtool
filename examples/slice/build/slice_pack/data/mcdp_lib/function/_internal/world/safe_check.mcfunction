execute if block ~ ~-1 ~ #mcdp_lib:unsafe_ground run return fail
summon minecraft:marker ~ ~ ~ {Tags:["mcdp_lib.pos"]}
data modify storage mcdp_lib:out pos set from entity @n[type=minecraft:marker,tag=mcdp_lib.pos] Pos
kill @e[type=minecraft:marker,tag=mcdp_lib.pos]
execute store result score #result mcdp_lib.out run data get storage mcdp_lib:out pos[1]
return 1
