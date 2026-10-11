#> __ns__:win/last_team/check - round ends when at most one team (distinct __ns__.tid) still has someone alive.
#> Free-for-all = every participant has its own tid (round/start_with); team games set equal tids in their start hook.
tag @e remove __ns__.unc
tag @e[tag=__ns__.alive] add __ns__.unc
scoreboard players set #teams __ns__.var 0
function __ns__:win/last_team/_count
tag @e remove __ns__.unc
return run execute if score #teams __ns__.var matches ..1
