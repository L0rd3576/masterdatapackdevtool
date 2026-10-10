#> __ns__:round/start_with {game, map, preset} - start a specific combination with the queued participants.
#> preset "default" = the manifest's default settings. Places the map first unless it is already placed and clean.
execute unless score #state __ns__.round matches 0 run return fail
$execute unless data storage __ns__:registry games.$(game).variants.$(preset) run return fail
$execute unless data storage __ns__:registry maps.$(map) run return fail
data remove storage __ns__:round current
data remove storage __ns__:round last_error
$data modify storage __ns__:round current.game set from storage __ns__:registry games.$(game)
data remove storage __ns__:round current.game.variants
$data modify storage __ns__:round current.map set from storage __ns__:registry maps.$(map)
$data modify storage __ns__:round current.preset set value "$(preset)"
$data modify storage __ns__:round current.settings set from storage __ns__:registry games.$(game).variants.$(preset).settings
$data modify storage __ns__:round current.rules set from storage __ns__:registry games.$(game).variants.$(preset).rules
$data modify storage __ns__:round current.rules_lib set from storage __ns__:registry games.$(game).variants.$(preset).rules_lib
execute store result score #n __ns__.round if entity @e[tag=__ns__.queued]
execute store result storage __ns__:round current.participants int 1 run scoreboard players get #n __ns__.round
tag @e[tag=__ns__.queued] add __ns__.in_round
tag @e[tag=__ns__.queued] add __ns__.alive
tag @e[tag=__ns__.queued] remove __ns__.queued
scoreboard players set @e[tag=__ns__.in_round] __ns__.score 0
scoreboard players set @e[tag=__ns__.in_round] __ns__.deaths 0
scoreboard players set #state __ns__.round 1
$execute if score #placed.$(map) __ns__.round matches 1 run return run function __ns__:round/begin
function __ns__:place/start
return 1
