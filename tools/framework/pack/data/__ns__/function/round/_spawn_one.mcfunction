#> __ns__:round/_spawn_one - internal, as a participant: teleport to the next shuffled spawn (reuse the list if
#> there are more participants than spawns; the spawn_count validator prevents that for valid maps)
execute unless data storage __ns__:round spawns[0] run data modify storage __ns__:round spawns set from storage __ns__:round current.map.spawns
function __lib__:world/tp_stored {storage:"__ns__:round",path:"spawns[0]"}
data remove storage __ns__:round spawns[0]
