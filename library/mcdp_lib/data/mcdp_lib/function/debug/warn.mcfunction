#> mcdp_lib:debug/warn
#> Purpose: debug/log at level 2 (warn).
#> Inputs: macro {msg:string}
#> Outputs: return 1 if shown, 0 if filtered
#> Effects: see debug/log
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:debug/warn {msg:"team empty"}
$return run function mcdp_lib:debug/log {level:2,msg:"$(msg)"}
