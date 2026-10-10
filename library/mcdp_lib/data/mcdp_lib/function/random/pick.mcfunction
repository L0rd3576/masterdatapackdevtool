#> mcdp_lib:random/pick
#> Purpose: Copy one uniformly random element of a storage list.
#> Inputs: macro {storage:string, path:string (list)}
#> Outputs: storage mcdp_lib:out random.value; return its index, or fail if the list is empty/missing
#> Effects: none on the source list
#> Context: any
#> Cost: macro (two calls)
#> Example: function mcdp_lib:random/pick {storage:"my:cfg",path:"maps"}
data remove storage mcdp_lib:out random.value
data remove storage mcdp_lib:internal pk
$data modify storage mcdp_lib:internal pk.src set from storage $(storage) $(path)
execute store result score #bound mcdp_lib.var if data storage mcdp_lib:internal pk.src[]
execute if score #bound mcdp_lib.var matches ..0 run return fail
function mcdp_lib:_internal/random/below
execute store result storage mcdp_lib:internal pk_args.i int 1 run scoreboard players get #r mcdp_lib.var
function mcdp_lib:_internal/random/pick_at with storage mcdp_lib:internal pk_args
return run scoreboard players get #r mcdp_lib.var
