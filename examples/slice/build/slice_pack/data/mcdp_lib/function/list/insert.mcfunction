#> mcdp_lib:list/insert
#> Purpose: Insert a value before an index (0 = front; creates the list if missing).
#> Inputs: macro {storage:string, path:string, index:int}; value in storage mcdp_lib:in value
#> Outputs: return 1, or fail if the index is out of range
#> Effects: modifies the list
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:list/insert {storage:"my:game",path:"queue",index:0}
$execute unless data storage $(storage) $(path) run data modify storage $(storage) $(path) set value []
$execute store success score #ok mcdp_lib.var run data modify storage $(storage) $(path) insert $(index) from storage mcdp_lib:in value
execute if score #ok mcdp_lib.var matches 0 run return fail
return 1
