#> slice:round/start_with {game, map, preset} - start a specific combination with the queued participants.
#> preset "default" = the manifest's default settings. Places the map first unless it is already placed and clean.
execute unless score #state slice.round matches 0 run return fail
$execute unless data storage slice:registry games.$(game).variants.$(preset) run return fail
$execute unless data storage slice:registry maps.$(map) run return fail
data remove storage slice:round current
data remove storage slice:round last_error
$data modify storage slice:round current.game set from storage slice:registry games.$(game)
data remove storage slice:round current.game.variants
$data modify storage slice:round current.map set from storage slice:registry maps.$(map)
$data modify storage slice:round current.preset set value "$(preset)"
$data modify storage slice:round current.settings set from storage slice:registry games.$(game).variants.$(preset).settings
$data modify storage slice:round current.rules set from storage slice:registry games.$(game).variants.$(preset).rules
$data modify storage slice:round current.rules_lib set from storage slice:registry games.$(game).variants.$(preset).rules_lib
execute store result score #n slice.round if entity @e[tag=slice.queued]
execute store result storage slice:round current.participants int 1 run scoreboard players get #n slice.round
tag @e[tag=slice.queued] add slice.in_round
tag @e[tag=slice.queued] add slice.alive
tag @e[tag=slice.queued] remove slice.queued
scoreboard players set @e[tag=slice.in_round] slice.score 0
scoreboard players set @e[tag=slice.in_round] slice.deaths 0
scoreboard players set #state slice.round 1
$execute if score #placed.$(map) slice.round matches 1 run return run function slice:round/begin
function slice:place/start
return 1
