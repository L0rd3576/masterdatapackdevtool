#> mcdp_lib:debug/trace
#> Purpose: debug/log at level 4 (trace/debug).
#> Inputs: macro {msg:string}
#> Outputs: return 1 if shown, 0 if filtered
#> Effects: see debug/log
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:debug/trace {msg:"tick"}
$return run function mcdp_lib:debug/log {level:4,msg:"$(msg)"}
