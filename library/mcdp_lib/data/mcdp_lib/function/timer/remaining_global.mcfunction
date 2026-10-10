#> mcdp_lib:timer/remaining_global
#> Purpose: Ticks left on the global timer (0 if not running).
#> Inputs: macro {name:string}
#> Outputs: return remaining ticks
#> Effects: none
#> Context: any
#> Cost: macro
#> Example: execute store result score #left my.v run function mcdp_lib:timer/remaining_global {name:"my.round"}
$execute unless score #global $(name) matches 1.. run return 0
$return run scoreboard players get #global $(name)
