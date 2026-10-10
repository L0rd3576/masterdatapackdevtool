#> mcdp_lib:world/setblock
#> Purpose: Place one block.
#> Inputs: macro {x,y,z:int, block:string (block state, may include {nbt})}
#> Outputs: return 1 if changed, else 0
#> Effects: changes a block
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:world/setblock {x:0,y:-60,z:0,block:"minecraft:gold_block"}
$execute store success score #result mcdp_lib.out run setblock $(x) $(y) $(z) $(block)
return run scoreboard players get #result mcdp_lib.out
