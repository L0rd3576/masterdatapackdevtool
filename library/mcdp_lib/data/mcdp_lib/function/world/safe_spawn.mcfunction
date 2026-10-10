#> mcdp_lib:world/safe_spawn
#> Purpose: Find the standing spot on top of column (x, z) and check it is not over a hazard (#mcdp_lib:unsafe_ground: lava, water, fire, cactus...).
#> Inputs: macro {x:int, z:int}
#> Outputs: storage mcdp_lib:out pos = [x,y,z] doubles, score #result mcdp_lib.out = y; return 1 if safe, fail if unsafe
#> Effects: summons and removes a marker
#> Context: any (column must be loaded)
#> Cost: macro
#> Example: execute if function mcdp_lib:world/safe_spawn {x:100,z:-40} run say ok
data remove storage mcdp_lib:out pos
$execute positioned $(x) 0 $(z) positioned over motion_blocking run return run function mcdp_lib:_internal/world/safe_check
return fail
