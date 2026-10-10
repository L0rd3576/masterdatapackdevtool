# Copies @s's saved entry into mcdp_lib:internal cur (cur is {} when nothing was saved).
data modify storage mcdp_lib:internal cur set value {}
data modify storage mcdp_lib:internal sv set value {}
data modify storage mcdp_lib:internal sv.uuid set from entity @s UUID
function mcdp_lib:_internal/player/peek_m with storage mcdp_lib:internal sv
