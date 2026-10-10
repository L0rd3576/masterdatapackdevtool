execute store result score #now mcdp_lib.var run time query gametime
data modify storage mcdp_lib:internal wait_scan set from storage mcdp_lib:internal wait
data modify storage mcdp_lib:internal wait set value []
function mcdp_lib:_internal/flow/wait_next
