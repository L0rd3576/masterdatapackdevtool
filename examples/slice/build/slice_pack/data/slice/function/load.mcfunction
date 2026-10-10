#> slice:load (framework; generated from tools/framework/pack by tools/build_pack.py)
#> Creates objectives, loads the compiled registry, keeps map slots loaded, runs minigame load hooks.
scoreboard objectives add slice.var dummy
scoreboard objectives add slice.cfg dummy
scoreboard objectives add slice.round dummy
scoreboard objectives add slice.score dummy
scoreboard objectives add slice.deaths deathCount
scoreboard objectives add slice.coins dummy {text:"Coins"}
function slice:_gen/registry
function slice:_gen/forceload
function mcdp_lib:timer/create {name:"slice.rtimer",callback:"slice:round/time_up"}
execute unless score #state slice.round matches 0.. run scoreboard players set #state slice.round 0
function slice:_gen/hooks_load
