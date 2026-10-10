#> __ns__:payout/_pot_split - internal: #amount /= number of winners (no winners: nobody gets the pot)
execute store result score #w __ns__.var if entity @e[tag=__ns__.winner]
execute if score #w __ns__.var matches 1.. run scoreboard players operation #amount __ns__.var /= #w __ns__.var
