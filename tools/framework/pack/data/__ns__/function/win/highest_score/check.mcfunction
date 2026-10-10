#> __ns__:win/highest_score/check - ends early when a participant reaches settings.score_to_win (if > 0);
#> otherwise the round runs until the time limit
execute store result score #goal __ns__.var run data get storage __ns__:round current.settings.score_to_win
execute if score #goal __ns__.var matches 1.. as @e[tag=__ns__.in_round] if score @s __ns__.score >= #goal __ns__.var run return 1
return fail
