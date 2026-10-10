#> mcdp_lib:player/random
#> Purpose: Give a tag to exactly one random entity matching a selector (removes the tag from everyone else first).
#> Inputs: macro {selector:string, tag:string}
#> Outputs: return 1, or fail if nothing matched
#> Effects: tag <tag> moves to the chosen entity
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:player/random {selector:"@a[gamemode=adventure]",tag:"my.it"}
$tag @e[tag=$(tag)] remove $(tag)
tag @e[tag=mcdp_lib.cand] remove mcdp_lib.cand
$tag $(selector) add mcdp_lib.cand
$execute store result score #result mcdp_lib.out run tag @e[tag=mcdp_lib.cand,sort=random,limit=1] add $(tag)
tag @e[tag=mcdp_lib.cand] remove mcdp_lib.cand
execute if score #result mcdp_lib.out matches ..0 run return fail
return 1
