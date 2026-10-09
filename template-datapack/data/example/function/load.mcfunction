# Runs on world load and on /reload (via #minecraft:load). Create every objective here.
scoreboard objectives add example.ticks dummy
scoreboard objectives add example.calls dummy
data modify storage example:state loaded set value 1b
