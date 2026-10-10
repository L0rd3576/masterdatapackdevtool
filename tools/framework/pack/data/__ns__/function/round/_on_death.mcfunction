#> __ns__:round/_on_death - internal, as a player who died: respawn or eliminate (rules.respawn)
scoreboard players set @s __ns__.deaths 0
execute if data storage __ns__:round current.rules{respawn:"respawn"} run return run function __ns__:round/respawn
function __ns__:round/eliminate
