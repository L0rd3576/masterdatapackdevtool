#> block_brawl start hook: reset counters, hand out shears and some wool to build with
scoreboard players set @a[tag=slice.in_round] slice.bb_white 0
scoreboard players set @a[tag=slice.in_round] slice.bb_orange 0
give @a[tag=slice.in_round] minecraft:shears
give @a[tag=slice.in_round] minecraft:white_wool 16
