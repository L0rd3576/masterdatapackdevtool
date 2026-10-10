# One registered timer: decrement running instances, then fire callbacks for the ones that reached 0.
$execute if data storage mcdp_lib:internal timers[{name:"$(name)",paused:1b}] run return 0
$scoreboard players remove @e[scores={$(name)=1..},tag=!mcdp_lib.paused.$(name)] $(name) 1
$execute as @e[scores={$(name)=0}] run tag @s add mcdp_lib.expired
$scoreboard players reset @e[tag=mcdp_lib.expired] $(name)
$execute as @e[tag=mcdp_lib.expired] at @s run function mcdp_lib:_internal/timer/fire {callback:"$(callback)"}
$execute if score #global $(name) matches 1.. run scoreboard players remove #global $(name) 1
$execute if score #global $(name) matches 0 run function mcdp_lib:_internal/timer/fire_global {name:"$(name)",callback:"$(callback)"}
