#> slice:round/_spawn_one - internal, as a participant: teleport to the next shuffled spawn (reuse the list if
#> there are more participants than spawns; the spawn_count validator prevents that for valid maps)
execute unless data storage slice:round spawns[0] run data modify storage slice:round spawns set from storage slice:round current.map.spawns
function mcdp_lib:world/tp_stored {storage:"slice:round",path:"spawns[0]"}
data remove storage slice:round spawns[0]
