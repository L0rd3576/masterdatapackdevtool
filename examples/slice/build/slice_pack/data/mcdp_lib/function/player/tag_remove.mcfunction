#> mcdp_lib:player/tag_remove
#> Purpose: Remove a tag from every entity matching a selector.
#> Inputs: macro {selector:string, tag:string}
#> Outputs: return the number of entities that lost the tag
#> Effects: removes the tag
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:player/tag_remove {selector:"@e",tag:"my.alive"}
$execute store result score #result mcdp_lib.out run tag $(selector) remove $(tag)
return run scoreboard players get #result mcdp_lib.out
