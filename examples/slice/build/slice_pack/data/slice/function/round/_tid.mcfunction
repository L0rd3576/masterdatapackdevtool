#> slice:round/_tid - internal: as a participant at round start: unique team id slice.tid 1..n (free-for-all).
#> Team games overwrite slice.tid in their start hook (same tid = same team for win condition last_team).
scoreboard players add #tid slice.var 1
scoreboard players operation @s slice.tid = #tid slice.var
