#> mcdp_lib:fsm/define
#> Purpose: Create a state machine from mcdp_lib:in fsm and enter its initial state (runs its enter function).
#> Inputs: macro {machine:string (letters, digits, _ only)}; storage mcdp_lib:in fsm = {initial:"lobby", states:{lobby:{enter:"my:lobby/enter", tick:"my:lobby/tick", exit:"my:lobby/exit", next:["game"]}, game:{...}}} (every key of a state is optional; next limits allowed transitions)
#> Outputs: return 1
#> Effects: writes storage mcdp_lib:internal fsm.<machine>; calls the initial enter function
#> Context: enter/exit/tick run in the caller's context
#> Cost: macro (setup)
#> Example: function mcdp_lib:fsm/define {machine:"game"}
$data modify storage mcdp_lib:internal fsm.$(machine) set value {name:"$(machine)",state:"",cur:{}}
$data modify storage mcdp_lib:internal fsm.$(machine).def set from storage mcdp_lib:in fsm
$data modify storage mcdp_lib:internal fsm_args set value {machine:"$(machine)"}
$data modify storage mcdp_lib:internal fsm_args.state set from storage mcdp_lib:internal fsm.$(machine).def.initial
function mcdp_lib:_internal/fsm/go with storage mcdp_lib:internal fsm_args
return 1
