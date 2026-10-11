#> slice:win/last_team/_count - internal: count one team per call (stops at 2, enough for the check), recurse
execute unless entity @e[tag=slice.unc] run return 0
scoreboard players add #teams slice.var 1
execute if score #teams slice.var matches 2.. run return 0
execute as @e[tag=slice.unc,limit=1] run function slice:win/last_team/_take
function slice:win/last_team/_count
