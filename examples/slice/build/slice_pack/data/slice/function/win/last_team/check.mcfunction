#> slice:win/last_team/check - round ends when at most one team (distinct slice.tid) still has someone alive.
#> Free-for-all = every participant has its own tid (round/start_with); team games set equal tids in their start hook.
tag @e remove slice.unc
tag @e[tag=slice.alive] add slice.unc
scoreboard players set #teams slice.var 0
function slice:win/last_team/_count
tag @e remove slice.unc
return run execute if score #teams slice.var matches ..1
