#> team_clash tick hook: eliminate every alive participant tagged slice.out_next in this tick (stands for a hazard
#> check; several eliminations in one tick = a same-tick tie for win condition last_team)
execute as @e[tag=slice.alive,tag=slice.out_next] run function slice:round/eliminate
tag @e[tag=slice.out_next] remove slice.out_next
