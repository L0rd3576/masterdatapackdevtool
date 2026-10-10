# Moves @s's saved entry (created if missing) into mcdp_lib:internal cur; close puts it back.
execute unless data storage mcdp_lib:internal saved run data modify storage mcdp_lib:internal saved set value []
data modify storage mcdp_lib:internal sv set value {}
data modify storage mcdp_lib:internal sv.uuid set from entity @s UUID
function mcdp_lib:_internal/player/open_m with storage mcdp_lib:internal sv
