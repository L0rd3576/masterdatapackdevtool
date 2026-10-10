#> __ns__:round/tick - internal: every tick while a round runs
function __ns__:round/hook {hook:"tick"}
execute as @a[tag=__ns__.alive,scores={__ns__.deaths=1..}] run function __ns__:round/_on_death
execute if score #state __ns__.round matches 2 run function __ns__:round/_win_check with storage __ns__:round current.game
