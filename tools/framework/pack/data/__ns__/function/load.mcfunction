#> __ns__:load (framework; generated from tools/framework/pack by tools/build_pack.py)
#> Creates objectives, loads the compiled registry, keeps map slots loaded, runs minigame load hooks.
scoreboard objectives add __ns__.var dummy
scoreboard objectives add __ns__.cfg dummy
scoreboard objectives add __ns__.round dummy
scoreboard objectives add __ns__.score dummy
scoreboard objectives add __ns__.deaths deathCount
scoreboard objectives add __ns__.__currency__ dummy {text:"__currency_name__"}
function __ns__:_gen/registry
function __ns__:_gen/forceload
function __lib__:timer/create {name:"__ns__.rtimer",callback:"__ns__:round/time_up"}
execute unless score #state __ns__.round matches 0.. run scoreboard players set #state __ns__.round 0
function __ns__:_gen/hooks_load
