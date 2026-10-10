#> mcdp_lib:msg/countdown
#> Purpose: Show "<label><seconds left>" once per second, then call a function when it reaches 0.
#> Inputs: macro {name:string (id, no spaces), seconds:int, targets:string, display:string (title|subtitle|actionbar), label:string (no double quotes), callback:string}
#> Outputs: score #cd.<name> mcdp_lib.var = last second shown; return 1
#> Effects: registers the countdown (same name replaces it); callback runs exactly seconds*20 ticks later, as the server
#> Context: any
#> Cost: macro (setup); per tick 1-3 macro calls per running countdown
#> Example: function mcdp_lib:msg/countdown {name:"start",seconds:10,targets:"@a",display:"actionbar",label:"Starting in ",callback:"my:start_game"}
$data remove storage mcdp_lib:internal countdowns[{name:"$(name)"}]
$data modify storage mcdp_lib:internal countdowns append value {name:"$(name)",targets:"$(targets)",display:"$(display)",label:"$(label)",callback:"$(callback)"}
$scoreboard players set #cd.$(name) mcdp_lib.cd $(seconds)
$scoreboard players operation #cd.$(name) mcdp_lib.cd *= #20 mcdp_lib.var
return 1
