#> mcdp_lib:world/clone
#> Purpose: Copy a box so its lowest corner lands on (x,y,z).
#> Inputs: macro {x1,y1,z1,x2,y2,z2:int, x,y,z:int (destination), mode:string (replace|masked)}
#> Outputs: return the number of blocks cloned
#> Effects: changes blocks
#> Context: any (both areas loaded)
#> Cost: macro
#> Example: function mcdp_lib:world/clone {x1:0,y1:-60,z1:0,x2:4,y2:-56,z2:4,x:20,y:-60,z:0,mode:"replace"}
$return run clone $(x1) $(y1) $(z1) $(x2) $(y2) $(z2) $(x) $(y) $(z) $(mode)
