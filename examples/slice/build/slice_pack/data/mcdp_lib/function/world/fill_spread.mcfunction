#> mcdp_lib:world/fill_spread
#> Purpose: Queue a big fill that runs <layers> horizontal layers per game tick (bottom to top), then calls a function.
#> Inputs: macro {x1,y1,z1,x2,y2,z2:int, block:string (no double quotes), layers:int (>= 1; keep layers*area <= 32768), callback:string}
#> Outputs: return the number of queued jobs (jobs run one after another)
#> Effects: changes blocks over the next ticks; callback runs as the server when the job is done
#> Context: any (area must stay loaded, e.g. forceload)
#> Cost: macro (setup); per tick one macro fill
#> Example: function mcdp_lib:world/fill_spread {x1:0,y1:-60,z1:0,x2:63,y2:20,z2:63,block:"minecraft:air",layers:4,callback:"my:arena_cleared"}
$data modify storage mcdp_lib:internal fill_jobs append value {x1:$(x1),y1:$(y1),z1:$(z1),x2:$(x2),y2:$(y2),z2:$(z2),block:"$(block)",layers:$(layers),callback:"$(callback)"}
execute store result score #a mcdp_lib.var run data get storage mcdp_lib:internal fill_jobs[-1].y1
execute store result score #b mcdp_lib.var run data get storage mcdp_lib:internal fill_jobs[-1].y2
execute if score #a mcdp_lib.var > #b mcdp_lib.var store result storage mcdp_lib:internal fill_jobs[-1].y1 int 1 run scoreboard players get #b mcdp_lib.var
execute if score #a mcdp_lib.var > #b mcdp_lib.var store result storage mcdp_lib:internal fill_jobs[-1].y2 int 1 run scoreboard players get #a mcdp_lib.var
return run data get storage mcdp_lib:internal fill_jobs
