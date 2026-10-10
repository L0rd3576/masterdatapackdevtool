#> mcdp_lib:debug/log
#> Purpose: Log a message if level <= the current debug level: chat to players tagged mcdp_lib.debug, and `say` to the server log when mcdp_lib:config debug_console is 1b.
#> Inputs: macro {level:int (1..4), msg:string (no double quotes)}
#> Outputs: storage mcdp_lib:out debug.last = msg; return 1 if shown, 0 if filtered
#> Effects: chat / server log output; score #count mcdp_lib.debug counts shown messages
#> Context: any
#> Cost: macro; when filtered out it stops after one score check
#> Example: function mcdp_lib:debug/log {level:3,msg:"round started"}
$execute unless score #level mcdp_lib.debug matches $(level).. run return 0
$data modify storage mcdp_lib:out debug.last set value "$(msg)"
scoreboard players add #count mcdp_lib.debug 1
$tellraw @a[tag=mcdp_lib.debug] [{text:"[mcdp L$(level)] ",color:"gray"},{text:"$(msg)"}]
$execute if data storage mcdp_lib:config {debug_console:1b} run say [mcdp L$(level)] $(msg)
return 1
