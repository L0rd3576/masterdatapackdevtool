#> mcdp_lib:timer/stop_global
#> Purpose: Cancel the global timer without running the callback.
#> Inputs: macro {name:string}
#> Outputs: return 1
#> Effects: resets #global's score <name>
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:timer/stop_global {name:"my.round"}
$scoreboard players reset #global $(name)
return 1
