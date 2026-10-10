#> mcdp_lib:item/give
#> Purpose: Give an item stack given as item syntax, e.g. "minecraft:stick[unbreakable={}]".
#> Inputs: macro {targets:string (players), item:string, count:int}
#> Outputs: return the number of players given to
#> Effects: gives items
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:item/give {targets:"@a",item:"minecraft:bread",count:8}
$return run give $(targets) $(item) $(count)
