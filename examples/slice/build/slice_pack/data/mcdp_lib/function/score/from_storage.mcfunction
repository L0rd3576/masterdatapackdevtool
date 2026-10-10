#> mcdp_lib:score/from_storage
#> Purpose: Copy a numeric storage value into a score, multiplied by scale and truncated to int.
#> Inputs: macro {storage:string, path:string, target:string, objective:string, scale:number (1 = unchanged)}
#> Outputs: the score; return the stored value (fail if the path is missing)
#> Effects: changes the score
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:score/from_storage {storage:"my:state",path:"round",target:"#round",objective:"my.game",scale:1}
$execute unless data storage $(storage) $(path) run return fail
$execute store result score $(target) $(objective) run data get storage $(storage) $(path) $(scale)
$return run scoreboard players get $(target) $(objective)
