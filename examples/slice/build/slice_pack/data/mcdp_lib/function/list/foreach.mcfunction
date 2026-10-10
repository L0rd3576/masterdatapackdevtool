#> mcdp_lib:list/foreach
#> Purpose: Call a function once per element of a storage list (iterates a copy; nested foreach is safe).
#> Inputs: macro {storage:string, path:string, function:string (function id)}
#> Outputs: callback sees storage mcdp_lib:out foreach.item and score #index mcdp_lib.out (read them first); compound items are also passed as macro arguments; return the number of calls
#> Effects: whatever the callback does
#> Context: callback runs in the caller's context (as/at preserved)
#> Cost: one macro call per element; about 4000 elements max per call (command chain limit)
#> Example: function mcdp_lib:list/foreach {storage:"my:cfg",path:"teams",function:"my:setup_team"}
$data modify storage mcdp_lib:internal fe append value {args:{fn:"$(function)"},list:[],i:0}
$data modify storage mcdp_lib:internal fe[-1].list set from storage $(storage) $(path)
function mcdp_lib:_internal/list/fe_step
execute store result score #n mcdp_lib.var run data get storage mcdp_lib:internal fe[-1].i
data remove storage mcdp_lib:internal fe[-1]
return run scoreboard players get #n mcdp_lib.var
