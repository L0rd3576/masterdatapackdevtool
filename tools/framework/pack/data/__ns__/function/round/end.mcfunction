#> __ns__:round/end - finish the running round: pick winners (win condition), run the end hook, pay out,
#> then tear down after end_delay ticks. Returns fail if no round is running.
execute unless score #state __ns__.round matches 2 run return fail
scoreboard players set #state __ns__.round 3
function __lib__:timer/stop_global {name:"__ns__.rtimer"}
tag @e remove __ns__.winner
function __ns__:round/_winners with storage __ns__:round current.game
function __ns__:round/hook {hook:"end"}
function __ns__:payout/run
tellraw @a[tag=__ns__.in_round] [{text:"Round over. Winner(s): ",color:"gold"},{selector:"@e[tag=__ns__.winner]",color:"yellow"}]
scoreboard players operation #end_wait __ns__.round = #end_delay __ns__.cfg
execute if score #end_wait __ns__.round matches ..0 run function __ns__:round/teardown
return 1
