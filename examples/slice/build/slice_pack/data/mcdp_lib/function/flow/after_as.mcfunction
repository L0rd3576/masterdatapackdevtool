#> mcdp_lib:flow/after_as
#> Purpose: Call a function N ticks later as/at @s (skipped if @s is gone by then).
#> Inputs: macro {ticks:int (>= 1), function:string}
#> Outputs: return 1
#> Effects: gives @s a unique mcdp_lib.id score if missing; queues the call in storage mcdp_lib:internal wait
#> Context: as an entity (@s)
#> Cost: macro (setup); per tick one loop over the queue while it is not empty
#> Example: execute as @p run function mcdp_lib:flow/after_as {ticks:40,function:"my:explode"}
execute unless score @s mcdp_lib.id matches 1.. run function mcdp_lib:player/uid
execute store result score #due mcdp_lib.var run time query gametime
$scoreboard players add #due mcdp_lib.var $(ticks)
# tick functions see the game time of the previous tick (verified by tests/flow.test.json)
scoreboard players remove #due mcdp_lib.var 1
$data modify storage mcdp_lib:internal wait append value {fn:"$(function)"}
execute store result storage mcdp_lib:internal wait[-1].due int 1 run scoreboard players get #due mcdp_lib.var
execute store result storage mcdp_lib:internal wait[-1].id int 1 run scoreboard players get @s mcdp_lib.id
return 1
