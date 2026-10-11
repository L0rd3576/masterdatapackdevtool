#> __ns__:win/last_team/winners - every participant (alive or eliminated) whose team still has someone alive wins
#> (time-up: all teams with survivors). Nobody alive: the teams of everyone eliminated in this tick win (same-tick tie).
execute as @e[tag=__ns__.alive] run function __ns__:win/last_team/_mark
execute unless entity @e[tag=__ns__.alive] as @e[tag=__ns__.elim_now] run function __ns__:win/last_team/_mark
