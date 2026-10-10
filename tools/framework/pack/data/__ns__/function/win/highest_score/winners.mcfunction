#> __ns__:win/highest_score/winners - participants with the highest __ns__.score win (ties share; nobody if all 0)
scoreboard players set #max __ns__.var 0
execute as @e[tag=__ns__.in_round] run scoreboard players operation #max __ns__.var > @s __ns__.score
execute if score #max __ns__.var matches 1.. as @e[tag=__ns__.in_round] if score @s __ns__.score = #max __ns__.var run tag @s add __ns__.winner
