scoreboard players operation #d2 zp.v = #dx zp.v
scoreboard players operation #d2 zp.v *= #dx zp.v
scoreboard players operation #t zp.v = #dz zp.v
scoreboard players operation #t zp.v *= #dz zp.v
scoreboard players operation #d2 zp.v += #t zp.v
execute if score #d2 zp.v > #r2 zp.v if score #d2 zp.v <= #Rb2 zp.v if score #mode zp.v matches 1 run setblock ~ ~ ~ minecraft:air
execute if score #d2 zp.v > #r2 zp.v if score #d2 zp.v <= #Rb2 zp.v if score #mode zp.v matches 2 unless block ~ ~ ~ minecraft:air run setblock ~ ~ ~ minecraft:lava
scoreboard players add #dx zp.v 1
execute if score #dx zp.v <= #R zp.v positioned ~1 ~ ~ run function zp:zone/_cell
