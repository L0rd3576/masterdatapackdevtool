scoreboard players operation #dx zp.v = #R zp.v
scoreboard players operation #dx zp.v *= #neg1 zp.v
function zp:zone/_cell
scoreboard players add #dz zp.v 1
execute if score #dz zp.v <= #R zp.v positioned ~ ~ ~1 run function zp:zone/_row
