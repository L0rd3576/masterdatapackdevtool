$execute if data storage mcdp_lib:internal fsm.$(machine).cur.exit run function mcdp_lib:_internal/fsm/call_key {machine:"$(machine)",key:"exit"}
$data modify storage mcdp_lib:internal fsm.$(machine).state set value "$(state)"
$data modify storage mcdp_lib:internal fsm.$(machine).cur set value {}
$data modify storage mcdp_lib:internal fsm.$(machine).cur set from storage mcdp_lib:internal fsm.$(machine).def.states.$(state)
$execute if data storage mcdp_lib:internal fsm.$(machine).cur.enter run function mcdp_lib:_internal/fsm/call_key {machine:"$(machine)",key:"enter"}
