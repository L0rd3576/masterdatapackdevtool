#> mcdp_lib:list/remove
#> Purpose: Remove the element at an index (negative counts from the end).
#> Inputs: macro {storage:string, path:string, index:int}
#> Outputs: storage mcdp_lib:out value = removed element; return 1, or fail if out of range
#> Effects: modifies the list
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:list/remove {storage:"my:game",path:"queue",index:2}
data remove storage mcdp_lib:out value
$execute unless data storage $(storage) $(path)[$(index)] run return fail
$data modify storage mcdp_lib:out value set from storage $(storage) $(path)[$(index)]
$data remove storage $(storage) $(path)[$(index)]
return 1
