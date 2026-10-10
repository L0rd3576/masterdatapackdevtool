#> __ns__:payout/run - internal: award __ns__.__currency__ from the minigame's payout block (n = participants)
#> linear: winners get base + per_participant*n; pot: that amount split evenly between winners; all get participation
execute store result score #base __ns__.var run data get storage __ns__:round current.game.payout.base
execute store result score #amount __ns__.var run data get storage __ns__:round current.game.payout.per_participant
execute store result score #part __ns__.var run data get storage __ns__:round current.game.payout.participation
scoreboard players operation #amount __ns__.var *= #n __ns__.round
scoreboard players operation #amount __ns__.var += #base __ns__.var
execute if data storage __ns__:round current.game.payout{type:"pot"} run function __ns__:payout/_pot_split
execute store result storage __ns__:round last_payout.winner int 1 run scoreboard players get #amount __ns__.var
execute store result storage __ns__:round last_payout.participation int 1 run scoreboard players get #part __ns__.var
execute as @e[tag=__ns__.winner] run scoreboard players operation @s __ns__.__currency__ += #amount __ns__.var
execute as @e[tag=__ns__.in_round] run scoreboard players operation @s __ns__.__currency__ += #part __ns__.var
