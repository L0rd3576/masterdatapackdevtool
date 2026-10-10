#> slice:win/highest_score/winners - participants with the highest slice.score win (ties share; nobody if all 0)
scoreboard players set #max slice.var 0
execute as @e[tag=slice.in_round] run scoreboard players operation #max slice.var > @s slice.score
execute if score #max slice.var matches 1.. as @e[tag=slice.in_round] if score @s slice.score = #max slice.var run tag @s add slice.winner
