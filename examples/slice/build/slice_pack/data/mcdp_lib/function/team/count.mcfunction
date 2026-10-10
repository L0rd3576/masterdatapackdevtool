#> mcdp_lib:team/count
#> Purpose: Number of loaded entities (players included) on a team.
#> Inputs: macro {name:string}
#> Outputs: score #result mcdp_lib.out; return the count
#> Effects: none
#> Context: any
#> Cost: macro
#> Example: execute store result score #reds my.game run function mcdp_lib:team/count {name:"my.red"}
$execute store result score #result mcdp_lib.out if entity @e[team=$(name)]
return run scoreboard players get #result mcdp_lib.out
