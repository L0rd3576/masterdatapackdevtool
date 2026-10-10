#> mcdp_lib:score/clamp
#> Purpose: Clamp a score in place to [min, max].
#> Inputs: macro {target:string (one holder), objective:string, min:int, max:int}
#> Outputs: return the clamped value
#> Effects: changes the score
#> Context: any
#> Cost: macro; scoreboard-only version: mcdp_lib:math/clamp
#> Example: function mcdp_lib:score/clamp {target:"@s",objective:"my.mana",min:0,max:100}
$scoreboard players set #lo mcdp_lib.var $(min)
$scoreboard players set #hi mcdp_lib.var $(max)
$scoreboard players operation $(target) $(objective) > #lo mcdp_lib.var
$scoreboard players operation $(target) $(objective) < #hi mcdp_lib.var
$return run scoreboard players get $(target) $(objective)
