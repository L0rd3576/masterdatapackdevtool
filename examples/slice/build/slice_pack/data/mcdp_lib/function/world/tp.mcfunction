#> mcdp_lib:world/tp
#> Purpose: Teleport @s to coordinates in a dimension.
#> Inputs: macro {x:number, y:number, z:number, dimension:string (e.g. "minecraft:overworld")}
#> Outputs: return 1
#> Effects: teleports @s
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @a run function mcdp_lib:world/tp {x:0,y:100,z:0,dimension:"minecraft:overworld"}
$execute in $(dimension) run tp @s $(x) $(y) $(z)
return 1
