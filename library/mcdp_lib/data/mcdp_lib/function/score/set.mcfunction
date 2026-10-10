#> mcdp_lib:score/set
#> Purpose: Set a score.
#> Inputs: macro {target:string (one holder, e.g. "@s" or "#x"), objective:string, value:int}
#> Outputs: return the new value
#> Effects: changes the score
#> Context: any (@s needs an executor)
#> Cost: macro; in hot code write `scoreboard players set` directly
#> Example: function mcdp_lib:score/set {target:"#round",objective:"my.game",value:1}
$scoreboard players set $(target) $(objective) $(value)
$return run scoreboard players get $(target) $(objective)
