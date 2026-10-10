#> mcdp_lib:world/fill
#> Purpose: Fill a box with a block (at most max_block_modifications = 32768 blocks per call by default).
#> Inputs: macro {x1,y1,z1,x2,y2,z2:int, block:string (block state), mode:string (replace|destroy|hollow|keep|outline)}
#> Outputs: return the number of blocks changed
#> Effects: changes blocks
#> Context: any (area must be loaded)
#> Cost: macro; for big boxes use mcdp_lib:world/fill_spread
#> Example: function mcdp_lib:world/fill {x1:0,y1:-60,z1:0,x2:9,y2:-60,z2:9,block:"minecraft:stone",mode:"replace"}
$return run fill $(x1) $(y1) $(z1) $(x2) $(y2) $(z2) $(block) $(mode)
