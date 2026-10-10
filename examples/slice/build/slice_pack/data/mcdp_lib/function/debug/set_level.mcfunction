#> mcdp_lib:debug/set_level
#> Purpose: Choose which log messages are shown: 0 off, 1 error, 2 warn, 3 info, 4 trace.
#> Inputs: macro {level:int}
#> Outputs: return the level
#> Effects: sets score #level mcdp_lib.debug (persists)
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:debug/set_level {level:3}
$scoreboard players set #level mcdp_lib.debug $(level)
$return $(level)
