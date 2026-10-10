#> mcdp_lib:list/pop
#> Purpose: Remove and return the last element (stack pop).
#> Inputs: macro {storage:string, path:string}
#> Outputs: storage mcdp_lib:out value; return 1, or fail if the list is empty
#> Effects: modifies the list
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:list/pop {storage:"my:game",path:"stack"}
data remove storage mcdp_lib:out value
$execute unless data storage $(storage) $(path)[-1] run return fail
$data modify storage mcdp_lib:out value set from storage $(storage) $(path)[-1]
$data remove storage $(storage) $(path)[-1]
return 1
