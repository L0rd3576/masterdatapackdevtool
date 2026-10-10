#> mcdp_lib:timer/resume
#> Purpose: Resume a timer paused with mcdp_lib:timer/pause.
#> Inputs: macro {name:string}
#> Outputs: return 1, or fail if the timer is not registered
#> Effects: sets paused:0b in the registry
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:timer/resume {name:"my.round"}
$execute unless data storage mcdp_lib:internal timers[{name:"$(name)"}] run return fail
$data modify storage mcdp_lib:internal timers[{name:"$(name)"}].paused set value 0b
return 1
