#> mcdp_lib:timer/create
#> Purpose: Register a countdown timer/cooldown (objective <name>) ticked by the library every game tick.
#> Inputs: macro {name:string (objective name = timer id), callback:string (function id run on expiry; "mcdp_lib:noop" for none)}
#> Outputs: return 1
#> Effects: creates objective <name>; adds/replaces the registry entry in storage mcdp_lib:internal timers
#> Context: any; the callback runs as/at each expired entity, or as the server for the #global timer
#> Cost: macro (setup); per tick one macro call per registered timer plus 4 selector scans
#> Example: function mcdp_lib:timer/create {name:"my.dash_cd",callback:"my:dash_ready"}
$scoreboard objectives add $(name) dummy
$data remove storage mcdp_lib:internal timers[{name:"$(name)"}]
$data modify storage mcdp_lib:internal timers append value {name:"$(name)",callback:"$(callback)",paused:0b}
return 1
