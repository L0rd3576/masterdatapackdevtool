execute unless data storage mcdp_lib:internal fe[-1].list[0] run return 0
data modify storage mcdp_lib:out foreach.item set from storage mcdp_lib:internal fe[-1].list[0]
data remove storage mcdp_lib:internal fe[-1].list[0]
execute store result score #index mcdp_lib.out run data get storage mcdp_lib:internal fe[-1].i
# fe[-1].c marks a compound item (a path like fe[-1]{c:1b} is invalid: no filter after an index)
data remove storage mcdp_lib:internal fe[-1].c
execute if data storage mcdp_lib:out foreach.item{} run data modify storage mcdp_lib:internal fe[-1].c set value 1b
execute if data storage mcdp_lib:internal fe[-1].c run function mcdp_lib:_internal/list/fe_call_with with storage mcdp_lib:internal fe[-1].args
execute unless data storage mcdp_lib:internal fe[-1].c run function mcdp_lib:_internal/call with storage mcdp_lib:internal fe[-1].args
execute store result score #i mcdp_lib.var run data get storage mcdp_lib:internal fe[-1].i
scoreboard players add #i mcdp_lib.var 1
execute store result storage mcdp_lib:internal fe[-1].i int 1 run scoreboard players get #i mcdp_lib.var
function mcdp_lib:_internal/list/fe_step
