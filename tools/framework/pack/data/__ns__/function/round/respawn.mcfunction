#> __ns__:round/respawn - as a participant: teleport to a random spawn of the current map and re-apply rules
function __lib__:random/pick {storage:"__ns__:round",path:"current.map.spawns"}
function __lib__:world/tp_stored {storage:"__lib__:out",path:"random.value"}
function __lib__:rules/apply_self
