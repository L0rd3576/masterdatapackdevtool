data modify storage mcdp_lib:internal fsm_call set value {}
$data modify storage mcdp_lib:internal fsm_call.fn set from storage mcdp_lib:internal fsm.$(machine).cur.$(key)
function mcdp_lib:_internal/call with storage mcdp_lib:internal fsm_call
