scoreboard players add @s p.last 0
execute store result score #now p.c run time query gametime
scoreboard players operation #gap p.c = #now p.c
scoreboard players operation #gap p.c -= @s p.last
scoreboard players operation @s p.last = #now p.c
execute if score #gap p.c matches ..5 run return 0
scoreboard players add #acts p.c 1
return 1
