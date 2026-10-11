#> slice:payout/run - internal: award slice.coins from the minigame's payout block (n = participants)
#> linear: winners get base + per_participant*n; pot: that amount split evenly between winners; all get participation
#> Both amounts are scaled by #mult_pct slice.round (percent, 100 = 1x; set to 100 at start, games may change it).
execute store result score #base slice.var run data get storage slice:round current.game.payout.base
execute store result score #amount slice.var run data get storage slice:round current.game.payout.per_participant
execute store result score #part slice.var run data get storage slice:round current.game.payout.participation
scoreboard players operation #amount slice.var *= #n slice.round
scoreboard players operation #amount slice.var += #base slice.var
scoreboard players operation #amount slice.var *= #mult_pct slice.round
scoreboard players operation #amount slice.var /= #100 slice.var
scoreboard players operation #part slice.var *= #mult_pct slice.round
scoreboard players operation #part slice.var /= #100 slice.var
execute if data storage slice:round current.game.payout{type:"pot"} run function slice:payout/_pot_split
execute store result storage slice:round last_payout.winner int 1 run scoreboard players get #amount slice.var
execute store result storage slice:round last_payout.participation int 1 run scoreboard players get #part slice.var
execute as @e[tag=slice.winner] run scoreboard players operation @s slice.coins += #amount slice.var
execute as @e[tag=slice.in_round] run scoreboard players operation @s slice.coins += #part slice.var
