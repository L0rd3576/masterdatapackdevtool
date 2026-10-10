#> slice:round/_start_timer - internal: global round timer = rules.time_limit_seconds * 20 ticks
data modify storage slice:tmp timer set value {name:"slice.rtimer",ticks:20}
execute store result storage slice:tmp timer.ticks int 20 run data get storage slice:round current.rules.time_limit_seconds
function mcdp_lib:timer/start_global with storage slice:tmp timer
