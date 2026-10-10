execute unless data storage mcdp_lib:internal kit[0] run return 0
execute if data storage mcdp_lib:internal kit[0].slot run function mcdp_lib:_internal/item/kit_slot with storage mcdp_lib:internal kit[0]
execute unless data storage mcdp_lib:internal kit[0].slot run function mcdp_lib:_internal/item/kit_give with storage mcdp_lib:internal kit[0]
data remove storage mcdp_lib:internal kit[0]
function mcdp_lib:_internal/item/kit_step
