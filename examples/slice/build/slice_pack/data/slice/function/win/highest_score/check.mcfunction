#> slice:win/highest_score/check - ends early when a participant reaches settings.score_to_win (if > 0);
#> otherwise the round runs until the time limit
execute store result score #goal slice.var run data get storage slice:round current.settings.score_to_win
execute if score #goal slice.var matches 1.. as @e[tag=slice.in_round] if score @s slice.score >= #goal slice.var run return 1
return fail
