#> mcdp_lib:timer/remaining
#> Purpose: Ticks left on @s's timer (0 if not running).
#> Inputs: macro {name:string}
#> Outputs: return remaining ticks
#> Effects: none
#> Context: as an entity (@s)
#> Cost: macro; hot path: read @s's score <name> directly
#> Example: execute store result score @s my.v run function mcdp_lib:timer/remaining {name:"my.dash_cd"}
$execute unless score @s $(name) matches 1.. run return 0
$return run scoreboard players get @s $(name)
