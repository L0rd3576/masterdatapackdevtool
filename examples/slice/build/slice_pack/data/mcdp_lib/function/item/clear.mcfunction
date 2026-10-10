#> mcdp_lib:item/clear
#> Purpose: Remove up to count items matching an item predicate (count 0 = only count them).
#> Inputs: macro {targets:string (players), item:string (item predicate, e.g. "*[custom_data~{a:1b}]"), count:int}
#> Outputs: return the number of matching items found/removed
#> Effects: removes items
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:item/clear {targets:"@a",item:"minecraft:tnt",count:64}
$return run clear $(targets) $(item) $(count)
