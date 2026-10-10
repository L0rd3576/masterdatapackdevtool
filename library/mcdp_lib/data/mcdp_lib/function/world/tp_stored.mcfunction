#> mcdp_lib:world/tp_stored
#> Purpose: Teleport @s to a location compound {x,y,z,dimension} kept in storage (e.g. a map's spawn list entry).
#> Inputs: macro {storage:string, path:string (to a compound {x,y,z,dimension})}
#> Outputs: return 1, or fail if the compound is missing
#> Effects: teleports @s
#> Context: as an entity (@s)
#> Cost: macro (two calls)
#> Example: execute as @a run function mcdp_lib:world/tp_stored {storage:"my:maps",path:"arena.spawn"}
$execute unless data storage $(storage) $(path) run return fail
$function mcdp_lib:world/tp with storage $(storage) $(path)
return 1
