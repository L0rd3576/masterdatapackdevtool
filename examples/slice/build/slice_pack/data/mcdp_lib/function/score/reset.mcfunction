#> mcdp_lib:score/reset
#> Purpose: Remove a score (target may be a selector, or * for every holder).
#> Inputs: macro {target:string, objective:string}
#> Outputs: return 1
#> Effects: resets the score(s)
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:score/reset {target:"*",objective:"my.kills"}
$scoreboard players reset $(target) $(objective)
return 1
