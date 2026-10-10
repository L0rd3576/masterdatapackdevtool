#> mcdp_lib:list/get
#> Purpose: Copy the element at an index (negative counts from the end).
#> Inputs: macro {storage:string, path:string, index:int}
#> Outputs: storage mcdp_lib:out value; return 1, or fail if out of range
#> Effects: none
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:list/get {storage:"my:game",path:"queue",index:-1}
data remove storage mcdp_lib:out value
$execute unless data storage $(storage) $(path)[$(index)] run return fail
$data modify storage mcdp_lib:out value set from storage $(storage) $(path)[$(index)]
return 1
