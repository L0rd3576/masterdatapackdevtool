#> mcdp_lib:flow/repeat
#> Purpose: Call a function N times in a row (capped by mcdp_lib:config max_repeat, default 1000); nesting is safe.
#> Inputs: macro {function:string, times:int}
#> Outputs: callback sees score #index mcdp_lib.out (0-based; read it first); return the number of calls made
#> Effects: whatever the callback does; mcdp_lib:flow/break inside the callback ends the loop after this call
#> Context: callback runs in the caller's context
#> Cost: macro per call; each call costs ~10 commands of the 65536 command budget
#> Example: function mcdp_lib:flow/repeat {function:"my:spawn_one",times:5}
$data modify storage mcdp_lib:internal rep append value {args:{fn:"$(function)"},i:0,n:$(times)}
execute store result score #n mcdp_lib.var run data get storage mcdp_lib:internal rep[-1].n
execute store result score #cap mcdp_lib.var run data get storage mcdp_lib:config max_repeat
execute if score #n mcdp_lib.var > #cap mcdp_lib.var run data modify storage mcdp_lib:internal rep[-1].n set from storage mcdp_lib:config max_repeat
function mcdp_lib:_internal/flow/rep_step
execute store result score #n mcdp_lib.var run data get storage mcdp_lib:internal rep[-1].i
data remove storage mcdp_lib:internal rep[-1]
return run scoreboard players get #n mcdp_lib.var
