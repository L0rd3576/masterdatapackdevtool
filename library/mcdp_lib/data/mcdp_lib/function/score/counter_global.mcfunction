#> mcdp_lib:score/counter_global
#> Purpose: Global counter: add amount to the fake player #global, creating the objective if needed.
#> Inputs: macro {objective:string, amount:int}
#> Outputs: return the new value
#> Effects: may create the objective; changes #global's score
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:score/counter_global {objective:"my.rounds",amount:1}
$scoreboard objectives add $(objective) dummy
$scoreboard players set #add mcdp_lib.var $(amount)
$scoreboard players operation #global $(objective) += #add mcdp_lib.var
$return run scoreboard players get #global $(objective)
