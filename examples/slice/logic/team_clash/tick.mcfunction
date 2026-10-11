#> team_clash tick hook: eliminate every alive participant tagged __ns__.out_next in this tick (stands for a hazard
#> check; several eliminations in one tick = a same-tick tie for win condition last_team)
execute as @e[tag=__ns__.alive,tag=__ns__.out_next] run function __ns__:round/eliminate
tag @e[tag=__ns__.out_next] remove __ns__.out_next
