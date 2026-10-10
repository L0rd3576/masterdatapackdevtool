#> mcdp_lib:team/leave
#> Purpose: Remove every entity matching a selector from its team.
#> Inputs: macro {selector:string}
#> Outputs: return the number of entities that left
#> Effects: changes team membership
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:team/leave {selector:"@a"}
$execute store result score #result mcdp_lib.out run team leave $(selector)
return run scoreboard players get #result mcdp_lib.out
