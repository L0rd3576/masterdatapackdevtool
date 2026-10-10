#> __ns__:win/survive/check - round ends early only if everyone is eliminated; survivors at time-out win
execute unless entity @e[tag=__ns__.alive] run return 1
return fail
