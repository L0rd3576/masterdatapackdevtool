#> mcdp_lib:random/pick_n
#> Purpose: Pick n distinct elements (by position) of a storage list in random order.
#> Inputs: macro {storage:string, path:string (list), n:int}
#> Outputs: storage mcdp_lib:out random.picked (list, min(n, length) items); return its length; fail if path missing
#> Effects: none on the source list
#> Context: any
#> Cost: one macro call per picked element
#> Example: function mcdp_lib:random/pick_n {storage:"my:cfg",path:"kits",n:3}
data modify storage mcdp_lib:out random.picked set value []
$execute unless data storage $(storage) $(path) run return fail
$data modify storage mcdp_lib:internal sh.src set from storage $(storage) $(path)
data modify storage mcdp_lib:internal sh.dst set value []
execute store result score #n mcdp_lib.var if data storage mcdp_lib:internal sh.src[]
$scoreboard players set #k mcdp_lib.var $(n)
function mcdp_lib:_internal/random/draw
data modify storage mcdp_lib:out random.picked set from storage mcdp_lib:internal sh.dst
return run data get storage mcdp_lib:out random.picked
