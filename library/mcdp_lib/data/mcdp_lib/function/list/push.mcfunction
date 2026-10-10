#> mcdp_lib:list/push
#> Purpose: Append a value to a storage list (creates the list if missing). Also "enqueue".
#> Inputs: macro {storage:string, path:string}; value in storage mcdp_lib:in value
#> Outputs: return the new length
#> Effects: modifies the list
#> Context: any
#> Cost: macro
#> Example: data modify storage mcdp_lib:in value set value {name:"Alex"}
$execute unless data storage $(storage) $(path) run data modify storage $(storage) $(path) set value []
$data modify storage $(storage) $(path) append from storage mcdp_lib:in value
$return run data get storage $(storage) $(path)
