#> __ns__:round/_abort_placing - internal: abort while the map is still being placed (nobody moved yet)
data modify storage __ns__:build queue set value []
tag @e remove __ns__.alive
tag @e remove __ns__.in_round
scoreboard players set #state __ns__.round 0
return 1
