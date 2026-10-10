#> mcdp_lib:msg/countdown_cancel
#> Purpose: Stop a countdown without calling its callback.
#> Inputs: macro {name:string}
#> Outputs: return 1, or fail if no such countdown runs
#> Effects: unregisters the countdown
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:msg/countdown_cancel {name:"start"}
$execute unless data storage mcdp_lib:internal countdowns[{name:"$(name)"}] run return fail
$data remove storage mcdp_lib:internal countdowns[{name:"$(name)"}]
$scoreboard players reset #cd.$(name) mcdp_lib.cd
return 1
