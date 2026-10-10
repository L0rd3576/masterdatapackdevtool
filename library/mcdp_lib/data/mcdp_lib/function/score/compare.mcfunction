#> mcdp_lib:score/compare
#> Purpose: Compare two scores with <, <=, =, >=, >.
#> Inputs: macro {a:string, a_objective:string, op:string, b:string, b_objective:string}
#> Outputs: return 1 if true, 0 if false (also 0 when a score is unset)
#> Effects: none
#> Context: any
#> Cost: macro; in hot code use `execute if score` directly
#> Example: execute if function mcdp_lib:score/compare {a:"@s",a_objective:"my.kills",op:">=",b:"#goal",b_objective:"my.game"} run say win
$execute if score $(a) $(a_objective) $(op) $(b) $(b_objective) run return 1
return 0
