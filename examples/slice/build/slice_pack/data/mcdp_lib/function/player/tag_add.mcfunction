#> mcdp_lib:player/tag_add
#> Purpose: Add a tag to every entity matching a selector.
#> Inputs: macro {selector:string, tag:string}
#> Outputs: return the number of entities that newly got the tag
#> Effects: adds the tag
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:player/tag_add {selector:"@a[team=red]",tag:"my.alive"}
$execute store result score #result mcdp_lib.out run tag $(selector) add $(tag)
return run scoreboard players get #result mcdp_lib.out
