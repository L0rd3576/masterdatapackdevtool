#> mcdp_lib:list/dequeue
#> Purpose: Remove and return the first element (queue pop; pair with list/push).
#> Inputs: macro {storage:string, path:string}
#> Outputs: storage mcdp_lib:out value; return 1, or fail if the list is empty
#> Effects: modifies the list
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:list/dequeue {storage:"my:game",path:"queue"}
data remove storage mcdp_lib:out value
$execute unless data storage $(storage) $(path)[0] run return fail
$data modify storage mcdp_lib:out value set from storage $(storage) $(path)[0]
$data remove storage $(storage) $(path)[0]
return 1
