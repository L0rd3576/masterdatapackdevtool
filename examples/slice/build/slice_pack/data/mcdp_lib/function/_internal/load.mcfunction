# Library setup (listed first in #minecraft:load). Idempotent: keeps config and registered timers across /reload.
scoreboard objectives add mcdp_lib.in dummy
scoreboard objectives add mcdp_lib.out dummy
scoreboard objectives add mcdp_lib.var dummy
scoreboard objectives add mcdp_lib.id dummy
scoreboard objectives add mcdp_lib.cd dummy
scoreboard objectives add mcdp_lib.debug dummy
scoreboard objectives add load.status dummy
scoreboard players set #mcdp_lib load.status 10000
scoreboard players set #neg1 mcdp_lib.var -1
scoreboard players set #20 mcdp_lib.var 20
scoreboard players set #1 mcdp_lib.var 1
data modify storage mcdp_lib:meta version set value "1.0.0"
execute unless data storage mcdp_lib:config max_repeat run data modify storage mcdp_lib:config max_repeat set value 1000
execute unless data storage mcdp_lib:config debug_console run data modify storage mcdp_lib:config debug_console set value 0b
execute unless data storage mcdp_lib:internal timers run data modify storage mcdp_lib:internal timers set value []
execute unless data storage mcdp_lib:internal countdowns run data modify storage mcdp_lib:internal countdowns set value []
execute unless data storage mcdp_lib:internal fill_jobs run data modify storage mcdp_lib:internal fill_jobs set value []
execute unless data storage mcdp_lib:internal wait run data modify storage mcdp_lib:internal wait set value []
data modify storage mcdp_lib:internal rep set value []
data modify storage mcdp_lib:internal fe set value []
execute unless score #level mcdp_lib.debug matches -2147483648.. run scoreboard players set #level mcdp_lib.debug 0
execute unless score #next mcdp_lib.id matches 1.. run scoreboard players set #next mcdp_lib.id 0
