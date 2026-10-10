#> mcdp_lib:team/remove
#> Purpose: Delete a team.
#> Inputs: macro {name:string}
#> Outputs: return 1
#> Effects: removes the team
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:team/remove {name:"my.red"}
$team remove $(name)
return 1
