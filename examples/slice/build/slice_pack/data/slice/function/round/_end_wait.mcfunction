#> slice:round/_end_wait - internal: count down project end_delay_ticks, then tear down
scoreboard players remove #end_wait slice.round 1
execute if score #end_wait slice.round matches ..0 run function slice:round/teardown
