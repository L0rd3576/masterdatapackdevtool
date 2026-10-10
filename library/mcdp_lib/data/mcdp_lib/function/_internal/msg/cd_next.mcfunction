execute unless data storage mcdp_lib:internal cd_scan[0] run return 0
function mcdp_lib:_internal/msg/cd_step with storage mcdp_lib:internal cd_scan[0]
data remove storage mcdp_lib:internal cd_scan[0]
function mcdp_lib:_internal/msg/cd_next
