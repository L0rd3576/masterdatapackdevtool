#> mcdp_lib:list/size
#> Purpose: Length of a storage list (0 if missing).
#> Inputs: macro {storage:string, path:string}
#> Outputs: return the length
#> Effects: none
#> Context: any
#> Cost: macro; inline alternative: execute store result score X run data get storage <s> <path>
#> Example: execute store result score #n my.v run function mcdp_lib:list/size {storage:"my:game",path:"queue"}
$execute unless data storage $(storage) $(path) run return 0
$return run data get storage $(storage) $(path)
