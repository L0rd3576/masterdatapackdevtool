#> slice:round/end - finish the running round: pick winners (win condition), run the end hook, pay out,
#> then tear down after end_delay ticks. Returns fail if no round is running.
execute unless score #state slice.round matches 2 run return fail
scoreboard players set #state slice.round 3
function mcdp_lib:timer/stop_global {name:"slice.rtimer"}
tag @e remove slice.winner
function slice:round/_winners with storage slice:round current.game
function slice:round/hook {hook:"end"}
function slice:payout/run
tellraw @a[tag=slice.in_round] [{text:"Round over. Winner(s): ",color:"gold"},{selector:"@e[tag=slice.winner]",color:"yellow"}]
scoreboard players operation #end_wait slice.round = #end_delay slice.cfg
execute if score #end_wait slice.round matches ..0 run function slice:round/teardown
return 1
