#> mcdp_lib:debug/info
#> Purpose: debug/log at level 3 (info).
#> Inputs: macro {msg:string}
#> Outputs: return 1 if shown, 0 if filtered
#> Effects: see debug/log
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:debug/info {msg:"round 2"}
$return run function mcdp_lib:debug/log {level:3,msg:"$(msg)"}
