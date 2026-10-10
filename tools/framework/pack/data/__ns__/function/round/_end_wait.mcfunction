#> __ns__:round/_end_wait - internal: count down project end_delay_ticks, then tear down
scoreboard players remove #end_wait __ns__.round 1
execute if score #end_wait __ns__.round matches ..0 run function __ns__:round/teardown
