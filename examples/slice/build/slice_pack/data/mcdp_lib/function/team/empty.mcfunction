#> mcdp_lib:team/empty
#> Purpose: Remove all members from a team (the team stays).
#> Inputs: macro {name:string}
#> Outputs: return 1
#> Effects: changes team membership
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:team/empty {name:"my.red"}
$team empty $(name)
return 1
