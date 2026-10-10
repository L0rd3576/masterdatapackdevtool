#> mcdp_lib:score/matches
#> Purpose: Test a score against a range such as "1..5", "..0" or "7".
#> Inputs: macro {target:string, objective:string, range:string}
#> Outputs: return 1 if it matches, else 0
#> Effects: none
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:score/matches {target:"#t",objective:"my.game",range:"1.."}
$execute if score $(target) $(objective) matches $(range) run return 1
return 0
