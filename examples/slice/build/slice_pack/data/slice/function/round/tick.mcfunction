#> slice:round/tick - internal: every tick while a round runs
function slice:round/hook {hook:"tick"}
execute as @a[tag=slice.alive,scores={slice.deaths=1..}] run function slice:round/_on_death
execute if score #state slice.round matches 2 run function slice:round/_win_check with storage slice:round current.game
