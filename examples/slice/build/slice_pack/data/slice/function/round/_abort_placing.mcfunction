#> slice:round/_abort_placing - internal: abort while the map is still being placed (nobody moved yet)
data modify storage slice:build queue set value []
tag @e remove slice.alive
tag @e remove slice.in_round
scoreboard players set #state slice.round 0
return 1
