#> mcdp_lib:player/tag_only
#> Purpose: Make a tag exclusive: remove it from all entities, then add it to the selector's matches.
#> Inputs: macro {selector:string, tag:string}
#> Outputs: return the number of entities that now have the tag
#> Effects: moves the tag
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:player/tag_only {selector:"@p",tag:"my.leader"}
$tag @e[tag=$(tag)] remove $(tag)
$execute store result score #result mcdp_lib.out run tag $(selector) add $(tag)
return run scoreboard players get #result mcdp_lib.out
