#> slice:round/respawn - as a participant: teleport to a random spawn of the current map and re-apply rules
function mcdp_lib:random/pick {storage:"slice:round",path:"current.map.spawns"}
function mcdp_lib:world/tp_stored {storage:"mcdp_lib:out",path:"random.value"}
function mcdp_lib:rules/apply_self
