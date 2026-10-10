#> __ns__:win/last_standing/check - round ends when at most one participant is still alive
execute store result score #alive __ns__.var if entity @e[tag=__ns__.alive]
return run execute if score #alive __ns__.var matches ..1
