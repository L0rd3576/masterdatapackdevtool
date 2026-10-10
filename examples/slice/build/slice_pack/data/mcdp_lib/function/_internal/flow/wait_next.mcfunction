execute unless data storage mcdp_lib:internal wait_scan[0] run return 0
execute store result score #due mcdp_lib.var run data get storage mcdp_lib:internal wait_scan[0].due
execute if score #due mcdp_lib.var > #now mcdp_lib.var run data modify storage mcdp_lib:internal wait append from storage mcdp_lib:internal wait_scan[0]
execute if score #due mcdp_lib.var <= #now mcdp_lib.var run function mcdp_lib:_internal/flow/wait_fire with storage mcdp_lib:internal wait_scan[0]
data remove storage mcdp_lib:internal wait_scan[0]
function mcdp_lib:_internal/flow/wait_next
