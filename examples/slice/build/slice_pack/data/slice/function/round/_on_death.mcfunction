#> slice:round/_on_death - internal, as a player who died: respawn or eliminate (rules.respawn)
scoreboard players set @s slice.deaths 0
execute if data storage slice:round current.rules{respawn:"respawn"} run return run function slice:round/respawn
function slice:round/eliminate
