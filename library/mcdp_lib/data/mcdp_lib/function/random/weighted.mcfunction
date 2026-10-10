#> mcdp_lib:random/weighted
#> Purpose: Weighted random pick from a list of {weight:int>=0, value:any}.
#> Inputs: macro {storage:string, path:string (list of {weight,value})}
#> Outputs: storage mcdp_lib:out random.value = chosen value; score #result mcdp_lib.out; return its index; fail if empty or all weights 0
#> Effects: none on the source list
#> Context: any
#> Cost: macro once, then scoreboard loop (about 2x list length steps)
#> Example: function mcdp_lib:random/weighted {storage:"my:cfg",path:"loot"}
data remove storage mcdp_lib:out random.value
$execute unless data storage $(storage) $(path)[0] run return fail
$data modify storage mcdp_lib:internal w.list set from storage $(storage) $(path)
data modify storage mcdp_lib:internal w.scan set from storage mcdp_lib:internal w.list
scoreboard players set #total mcdp_lib.var 0
function mcdp_lib:_internal/random/w_sum
execute if score #total mcdp_lib.var matches ..0 run return fail
scoreboard players operation #bound mcdp_lib.var = #total mcdp_lib.var
function mcdp_lib:_internal/random/below
scoreboard players set #idx mcdp_lib.var 0
return run function mcdp_lib:_internal/random/w_pick
