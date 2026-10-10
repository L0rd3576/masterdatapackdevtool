#> mcdp_lib:player/save_gamemode
#> Purpose: Remember a player's game mode.
#> Inputs: none
#> Outputs: return 1, or fail if @s is not a player
#> Effects: writes storage mcdp_lib:internal saved
#> Context: as a player (@s)
#> Cost: macro (UUID lookup)
#> Example: execute as @a run function mcdp_lib:player/save_gamemode
execute unless entity @s[type=minecraft:player] run return fail
function mcdp_lib:_internal/player/open
data modify storage mcdp_lib:internal cur.gm set from entity @s playerGameType
function mcdp_lib:_internal/player/close
return 1
