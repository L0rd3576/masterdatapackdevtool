execute unless data storage mcdp_lib:internal timer_scan[0] run return 0
function mcdp_lib:_internal/timer/step with storage mcdp_lib:internal timer_scan[0]
data remove storage mcdp_lib:internal timer_scan[0]
function mcdp_lib:_internal/timer/next
