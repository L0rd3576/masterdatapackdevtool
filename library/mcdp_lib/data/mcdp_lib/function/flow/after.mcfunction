#> mcdp_lib:flow/after
#> Purpose: Call a function after N ticks (schedule ... append: calling twice runs it twice).
#> Inputs: macro {ticks:int (>= 1), function:string}
#> Outputs: return 1
#> Effects: schedules the function; it runs as the server at world spawn (no @s; use flow/after_as to keep the entity)
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:flow/after {ticks:100,function:"my:round_end"}
$schedule function $(function) $(ticks)t append
return 1
