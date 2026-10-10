# Library per-tick work; each line costs one storage check while its feature is unused.
execute if data storage mcdp_lib:internal timers[0] run function mcdp_lib:_internal/timer/tick
execute if data storage mcdp_lib:internal countdowns[0] run function mcdp_lib:_internal/msg/countdown_tick
execute if data storage mcdp_lib:internal fill_jobs[0] run function mcdp_lib:_internal/world/fill_tick
execute if data storage mcdp_lib:internal wait[0] run function mcdp_lib:_internal/flow/wait_tick
