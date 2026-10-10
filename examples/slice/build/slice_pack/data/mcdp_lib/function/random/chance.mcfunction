#> mcdp_lib:random/chance
#> Purpose: Succeed with the given probability in percent.
#> Inputs: macro {percent:int 0..100}
#> Outputs: return 1 (hit) or 0 (miss)
#> Effects: none
#> Context: any
#> Cost: macro
#> Example: execute if function mcdp_lib:random/chance {percent:25} run function my:crit
execute store result score #r mcdp_lib.var run random value 1..100
$execute if score #r mcdp_lib.var matches ..$(percent) run return 1
return 0
