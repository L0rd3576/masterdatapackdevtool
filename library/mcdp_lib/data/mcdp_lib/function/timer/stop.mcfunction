#> mcdp_lib:timer/stop
#> Purpose: Cancel @s's timer without running the callback (also clears its pause).
#> Inputs: macro {name:string}
#> Outputs: return 1
#> Effects: resets @s's score <name>; removes tag mcdp_lib.paused.<name>
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @p run function mcdp_lib:timer/stop {name:"my.dash_cd"}
$scoreboard players reset @s $(name)
$tag @s remove mcdp_lib.paused.$(name)
return 1
