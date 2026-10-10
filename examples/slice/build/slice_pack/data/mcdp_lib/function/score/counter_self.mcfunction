#> mcdp_lib:score/counter_self
#> Purpose: Per-entity counter: add amount to @s on a dummy objective, creating the objective if needed.
#> Inputs: macro {objective:string, amount:int}
#> Outputs: return the new value
#> Effects: may create the objective; changes @s's score
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @a[tag=winner] run function mcdp_lib:score/counter_self {objective:"my.wins",amount:1}
$scoreboard objectives add $(objective) dummy
$scoreboard players set #add mcdp_lib.var $(amount)
$scoreboard players operation @s $(objective) += #add mcdp_lib.var
$return run scoreboard players get @s $(objective)
