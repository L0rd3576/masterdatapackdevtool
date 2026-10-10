#> mcdp_lib:timer/ready
#> Purpose: Cooldown check: 1 if @s has no running timer <name>, else 0.
#> Inputs: macro {name:string}
#> Outputs: return 1 (ready) or 0 (cooling down)
#> Effects: none
#> Context: as an entity (@s)
#> Cost: macro; hot path: `execute unless score @s <name> matches 1..`
#> Example: execute as @p if function mcdp_lib:timer/ready {name:"my.dash_cd"} run function my:dash
$execute if score @s $(name) matches 1.. run return 0
return 1
