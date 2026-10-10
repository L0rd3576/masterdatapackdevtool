#> mcdp_lib:item/clear_custom
#> Purpose: Remove every item tagged custom_data {mcdp_id:"<id>"} from players.
#> Inputs: macro {targets:string (players), id:string}
#> Outputs: return the number of items removed
#> Effects: removes items
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:item/clear_custom {targets:"@a",id:"wand"}
$return run clear $(targets) *[minecraft:custom_data~{mcdp_id:"$(id)"}]
