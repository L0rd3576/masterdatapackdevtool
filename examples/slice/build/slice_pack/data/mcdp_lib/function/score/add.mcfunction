#> mcdp_lib:score/add
#> Purpose: Add a (possibly negative) amount to a score; an unset score counts as 0.
#> Inputs: macro {target:string (one holder), objective:string, value:int}
#> Outputs: return the new value
#> Effects: changes the score
#> Context: any (@s needs an executor)
#> Cost: macro
#> Example: function mcdp_lib:score/add {target:"@s",objective:"my.coins",value:-5}
$scoreboard players set #add mcdp_lib.var $(value)
$scoreboard players operation $(target) $(objective) += #add mcdp_lib.var
$return run scoreboard players get $(target) $(objective)
