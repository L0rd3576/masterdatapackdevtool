#> slice:payout/_pot_split - internal: #amount /= number of winners (no winners: nobody gets the pot)
execute store result score #w slice.var if entity @e[tag=slice.winner]
execute if score #w slice.var matches 1.. run scoreboard players operation #amount slice.var /= #w slice.var
