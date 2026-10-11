summon minecraft:item ~ ~ ~ {Item:{id:"minecraft:stone",count:1},PickupDelay:0s,Tags:["p.ev"]}
$item replace entity @n[type=minecraft:item,tag=p.ev] contents from entity @s $(slot)
tag @e[type=minecraft:item,tag=p.ev] add p.evdone
tag @e[type=minecraft:item,tag=p.ev] remove p.ev
