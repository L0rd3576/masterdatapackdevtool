#> slice:win/last_team/winners - every participant (alive or eliminated) whose team still has someone alive wins
#> (time-up: all teams with survivors). Nobody alive: the teams of everyone eliminated in this tick win (same-tick tie).
execute as @e[tag=slice.alive] run function slice:win/last_team/_mark
execute unless entity @e[tag=slice.alive] as @e[tag=slice.elim_now] run function slice:win/last_team/_mark
