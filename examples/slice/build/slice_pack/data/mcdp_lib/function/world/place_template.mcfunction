#> mcdp_lib:world/place_template
#> Purpose: Place a structure template (data/<ns>/structure/<path>.nbt) at a position.
#> Inputs: macro {template:string (resource location), x,y,z:int}
#> Outputs: return 1 if placed, else 0
#> Effects: changes blocks/entities
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:world/place_template {template:"my:arena",x:0,y:-60,z:0}
$execute store success score #result mcdp_lib.out run place template $(template) $(x) $(y) $(z)
return run scoreboard players get #result mcdp_lib.out
