#> block_brawl start hook: reset counters, hand out shears and some wool to build with
scoreboard players set @a[tag=__ns__.in_round] __ns__.bb_white 0
scoreboard players set @a[tag=__ns__.in_round] __ns__.bb_orange 0
give @a[tag=__ns__.in_round] minecraft:shears
give @a[tag=__ns__.in_round] minecraft:white_wool 16
