#> mcdp_lib:item/custom
#> Purpose: Give a custom-named item tagged with custom_data {mcdp_id:"<id>"} so it can be detected later.
#> Inputs: macro {targets:string, item:string (item id), id:string, name:compound (text component, e.g. {text:"Wand",color:"gold"}), count:int}
#> Outputs: return the number of players given to
#> Effects: gives items
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:item/custom {targets:"@p",item:"minecraft:stick",id:"wand",name:{text:"Wand",italic:false},count:1}
$return run give $(targets) $(item)[minecraft:custom_name=$(name),minecraft:custom_data={mcdp_id:"$(id)"}] $(count)
