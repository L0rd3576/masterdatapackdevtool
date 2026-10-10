#> mcdp_lib:timer/start
#> Purpose: Start (or restart) a registered timer on @s; the callback fires after <ticks> game ticks.
#> Inputs: macro {name:string, ticks:int (>= 1)}
#> Outputs: return ticks
#> Effects: sets @s's score <name>
#> Context: as an entity (@s)
#> Cost: macro; hot path: `scoreboard players set @s <name> <ticks>` does the same
#> Example: execute as @p run function mcdp_lib:timer/start {name:"my.dash_cd",ticks:40}
$scoreboard players set @s $(name) $(ticks)
$return $(ticks)
