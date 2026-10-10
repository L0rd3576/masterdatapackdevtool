#> mcdp_lib:team/setup
#> Purpose: Create (or update) a team with color, friendly fire, collision and name tag rules.
#> Inputs: macro {name:string, color:string (team color, e.g. "red"), friendly_fire:bool (1b/0b), collision:string (always|never|pushOtherTeams|pushOwnTeam), nametag:string (always|never|hideForOtherTeams|hideForOwnTeam)}
#> Outputs: return 1
#> Effects: adds/modifies the team
#> Context: any
#> Cost: macro (setup)
#> Example: function mcdp_lib:team/setup {name:"my.red",color:"red",friendly_fire:0b,collision:"pushOtherTeams",nametag:"hideForOtherTeams"}
$team add $(name)
$team modify $(name) color $(color)
$scoreboard players set #ff mcdp_lib.var $(friendly_fire)
$execute if score #ff mcdp_lib.var matches 0 run team modify $(name) friendlyFire false
$execute if score #ff mcdp_lib.var matches 1 run team modify $(name) friendlyFire true
$team modify $(name) collisionRule $(collision)
$team modify $(name) nametagVisibility $(nametag)
return 1
