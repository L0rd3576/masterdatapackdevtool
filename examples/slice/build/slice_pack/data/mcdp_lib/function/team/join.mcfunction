#> mcdp_lib:team/join
#> Purpose: Put every entity matching a selector on a team.
#> Inputs: macro {name:string, selector:string}
#> Outputs: return the number of entities that joined
#> Effects: changes team membership
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:team/join {name:"my.red",selector:"@a[tag=my.red_pick]"}
$execute store result score #result mcdp_lib.out run team join $(name) $(selector)
return run scoreboard players get #result mcdp_lib.out
