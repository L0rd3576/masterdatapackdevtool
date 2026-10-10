#> mcdp_lib:timer/pause_self
#> Purpose: Pause only @s's instance of a timer.
#> Inputs: macro {name:string}
#> Outputs: return 1
#> Effects: adds tag mcdp_lib.paused.<name> to @s
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @p run function mcdp_lib:timer/pause_self {name:"my.dash_cd"}
$tag @s add mcdp_lib.paused.$(name)
return 1
