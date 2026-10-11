#> __ns__:round/_tid - internal: as a participant at round start: unique team id __ns__.tid 1..n (free-for-all).
#> Team games overwrite __ns__.tid in their start hook (same tid = same team for win condition last_team).
scoreboard players add #tid __ns__.var 1
scoreboard players operation @s __ns__.tid = #tid __ns__.var
