#> mcdp_lib:score/to_storage
#> Purpose: Copy a score into storage as an int.
#> Inputs: macro {target:string, objective:string, storage:string (resource location), path:string (NBT path)}
#> Outputs: storage <storage> <path> = score; return the score
#> Effects: writes storage
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:score/to_storage {target:"#round",objective:"my.game",storage:"my:state",path:"round"}
$execute store result storage $(storage) $(path) int 1 run scoreboard players get $(target) $(objective)
$return run scoreboard players get $(target) $(objective)
