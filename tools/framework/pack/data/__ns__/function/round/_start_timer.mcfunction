#> __ns__:round/_start_timer - internal: global round timer = rules.time_limit_seconds * 20 ticks
data modify storage __ns__:tmp timer set value {name:"__ns__.rtimer",ticks:20}
execute store result storage __ns__:tmp timer.ticks int 20 run data get storage __ns__:round current.rules.time_limit_seconds
function __lib__:timer/start_global with storage __ns__:tmp timer
