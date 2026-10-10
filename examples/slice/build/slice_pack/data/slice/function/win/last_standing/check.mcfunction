#> slice:win/last_standing/check - round ends when at most one participant is still alive
execute store result score #alive slice.var if entity @e[tag=slice.alive]
return run execute if score #alive slice.var matches ..1
