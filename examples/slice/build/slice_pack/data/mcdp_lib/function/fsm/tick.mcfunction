#> mcdp_lib:fsm/tick
#> Purpose: Run the current state's tick function (call it from your own tick function).
#> Inputs: macro {machine:string}
#> Outputs: return 1 if a tick function ran, else 0
#> Effects: whatever the state's tick function does
#> Context: tick function runs in the caller's context
#> Cost: macro, one call per tick (identical arguments)
#> Example: function mcdp_lib:fsm/tick {machine:"game"}
$execute unless data storage mcdp_lib:internal fsm.$(machine).cur.tick run return 0
$function mcdp_lib:_internal/fsm/call_tick with storage mcdp_lib:internal fsm.$(machine).cur
return 1
