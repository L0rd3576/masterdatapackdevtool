#> mcdp_lib:fsm/is
#> Purpose: Test whether a machine is in a given state.
#> Inputs: macro {machine:string, state:string}
#> Outputs: return 1 if yes, else 0
#> Effects: none
#> Context: any
#> Cost: macro
#> Example: execute if function mcdp_lib:fsm/is {machine:"game",state:"playing"} run function my:hud
$execute if data storage mcdp_lib:internal fsm.$(machine){state:"$(state)"} run return 1
return 0
