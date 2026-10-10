#> mcdp_lib:fsm/get
#> Purpose: Read the current state name of a machine.
#> Inputs: macro {machine:string}
#> Outputs: storage mcdp_lib:out fsm.state (string); return 1, or fail if the machine is unknown
#> Effects: none
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:fsm/get {machine:"game"}
data remove storage mcdp_lib:out fsm.state
$execute unless data storage mcdp_lib:internal fsm.$(machine) run return fail
$data modify storage mcdp_lib:out fsm.state set from storage mcdp_lib:internal fsm.$(machine).state
return 1
