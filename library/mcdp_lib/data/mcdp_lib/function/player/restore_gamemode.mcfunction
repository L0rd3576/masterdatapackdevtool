#> mcdp_lib:player/restore_gamemode
#> Purpose: Restore the game mode saved by save_gamemode.
#> Inputs: none
#> Outputs: return 1, or fail if @s is not a player or nothing was saved
#> Effects: changes @s's game mode
#> Context: as a player (@s)
#> Cost: macro (UUID lookup)
#> Example: execute as @a run function mcdp_lib:player/restore_gamemode
execute unless entity @s[type=minecraft:player] run return fail
function mcdp_lib:_internal/player/peek
execute unless data storage mcdp_lib:internal cur.gm run return fail
execute if data storage mcdp_lib:internal cur{gm:0} run gamemode survival @s
execute if data storage mcdp_lib:internal cur{gm:1} run gamemode creative @s
execute if data storage mcdp_lib:internal cur{gm:2} run gamemode adventure @s
execute if data storage mcdp_lib:internal cur{gm:3} run gamemode spectator @s
return 1
