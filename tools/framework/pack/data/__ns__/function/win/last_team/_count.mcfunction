#> __ns__:win/last_team/_count - internal: count one team per call (stops at 2, enough for the check), recurse
execute unless entity @e[tag=__ns__.unc] run return 0
scoreboard players add #teams __ns__.var 1
execute if score #teams __ns__.var matches 2.. run return 0
execute as @e[tag=__ns__.unc,limit=1] run function __ns__:win/last_team/_take
function __ns__:win/last_team/_count
