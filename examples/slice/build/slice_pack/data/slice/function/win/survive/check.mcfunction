#> slice:win/survive/check - round ends early only if everyone is eliminated; survivors at time-out win
execute unless entity @e[tag=slice.alive] run return 1
return fail
