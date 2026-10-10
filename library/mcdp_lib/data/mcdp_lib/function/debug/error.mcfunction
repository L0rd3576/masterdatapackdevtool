#> mcdp_lib:debug/error
#> Purpose: debug/log at level 1 (error).
#> Inputs: macro {msg:string}
#> Outputs: return 1 if shown, 0 if filtered
#> Effects: see debug/log
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:debug/error {msg:"no spawn points"}
$return run function mcdp_lib:debug/log {level:1,msg:"$(msg)"}
