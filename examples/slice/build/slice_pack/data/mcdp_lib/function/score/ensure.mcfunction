#> mcdp_lib:score/ensure
#> Purpose: Create a scoreboard objective if it does not exist yet (no-op if it does).
#> Inputs: macro {name:string, criteria:string}
#> Outputs: return 1
#> Effects: adds objective <name>
#> Context: any
#> Cost: macro (setup code)
#> Example: function mcdp_lib:score/ensure {name:"my.kills",criteria:"dummy"}
$scoreboard objectives add $(name) $(criteria)
return 1
