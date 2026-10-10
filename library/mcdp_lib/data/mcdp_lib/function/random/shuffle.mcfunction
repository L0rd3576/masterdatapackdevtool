#> mcdp_lib:random/shuffle
#> Purpose: Shuffle a storage list in place (uniform: repeatedly moves a random remaining element).
#> Inputs: macro {storage:string, path:string (list)}
#> Outputs: return the list length, or fail if the path is missing
#> Effects: rewrites the list
#> Context: any
#> Cost: one macro call per element; about 5000 elements max per call (command chain limit)
#> Example: function mcdp_lib:random/shuffle {storage:"my:game",path:"spawns"}
$execute unless data storage $(storage) $(path) run return fail
$data modify storage mcdp_lib:internal sh.src set from storage $(storage) $(path)
data modify storage mcdp_lib:internal sh.dst set value []
execute store result score #n mcdp_lib.var if data storage mcdp_lib:internal sh.src[]
scoreboard players set #k mcdp_lib.var 2147483647
function mcdp_lib:_internal/random/draw
$data modify storage $(storage) $(path) set from storage mcdp_lib:internal sh.dst
return run data get storage mcdp_lib:internal sh.dst
