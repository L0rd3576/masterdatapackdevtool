#> mcdp_lib:timer/start_global
#> Purpose: Start (or restart) the global instance of a registered timer (fake player #global).
#> Inputs: macro {name:string, ticks:int (>= 1)}
#> Outputs: return ticks
#> Effects: sets #global's score <name>
#> Context: any; callback runs without @s at the tick function's position
#> Cost: macro
#> Example: function mcdp_lib:timer/start_global {name:"my.round",ticks:6000}
$scoreboard players set #global $(name) $(ticks)
$return $(ticks)
