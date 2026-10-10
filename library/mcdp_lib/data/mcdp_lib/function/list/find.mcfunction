#> mcdp_lib:list/find
#> Purpose: Index of the first element exactly equal (same NBT type and value) to mcdp_lib:in value.
#> Inputs: macro {storage:string, path:string}; needle in storage mcdp_lib:in value
#> Outputs: return the index or -1; score #result mcdp_lib.out; fail if mcdp_lib:in value is missing
#> Effects: none
#> Context: any
#> Cost: macro once, then a storage loop
#> Example: data modify storage mcdp_lib:in value set value "lobby"
scoreboard players set #result mcdp_lib.out -1
execute unless data storage mcdp_lib:in value run return fail
data modify storage mcdp_lib:internal f.list set value []
$data modify storage mcdp_lib:internal f.list set from storage $(storage) $(path)
scoreboard players set #idx mcdp_lib.var 0
execute store result score #result mcdp_lib.out run function mcdp_lib:_internal/list/find_step
return run scoreboard players get #result mcdp_lib.out
