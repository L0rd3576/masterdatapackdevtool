#> mcdp_lib:fsm/set
#> Purpose: Transition to a state: runs the current state's exit, then the new state's enter.
#> Inputs: macro {machine:string, state:string}
#> Outputs: return 1, or fail if the machine/state is unknown or the transition is not in the current state's next list
#> Effects: changes the machine state; calls exit/enter functions
#> Context: exit/enter run in the caller's context
#> Cost: macro
#> Example: function mcdp_lib:fsm/set {machine:"game",state:"playing"}
$execute unless data storage mcdp_lib:internal fsm.$(machine) run return fail
$execute unless data storage mcdp_lib:internal fsm.$(machine).def.states.$(state) run return fail
$execute if data storage mcdp_lib:internal fsm.$(machine).cur.next unless data storage mcdp_lib:internal fsm.$(machine).cur{next:["$(state)"]} run return fail
$function mcdp_lib:_internal/fsm/go {machine:"$(machine)",state:"$(state)"}
return 1
