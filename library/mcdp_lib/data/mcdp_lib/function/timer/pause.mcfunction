#> mcdp_lib:timer/pause
#> Purpose: Pause every instance of a registered timer (entities and #global).
#> Inputs: macro {name:string}
#> Outputs: return 1, or fail if the timer is not registered
#> Effects: sets paused:1b in the registry
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:timer/pause {name:"my.round"}
$execute unless data storage mcdp_lib:internal timers[{name:"$(name)"}] run return fail
$data modify storage mcdp_lib:internal timers[{name:"$(name)"}].paused set value 1b
return 1
