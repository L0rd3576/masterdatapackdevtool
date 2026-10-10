#> mcdp_lib:rules/apply_self
#> Purpose: Apply the per-entity part of the active rules (game mode, block_break, effects) to @s, e.g. for players who join or respawn later.
#> Inputs: none (uses the struct stored by rules/apply)
#> Outputs: return 1, or fail if no rules are active
#> Effects: see rules/apply; tags @s mcdp_lib.ruled
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @a[tag=!mcdp_lib.ruled] run function mcdp_lib:rules/apply_self
execute unless data storage mcdp_lib:internal rules.active run return fail
tag @s add mcdp_lib.ruled
execute if entity @s[type=minecraft:player] if data storage mcdp_lib:internal rules.set.gamemode run function mcdp_lib:player/save_gamemode
execute if entity @s[type=minecraft:player] if data storage mcdp_lib:internal rules.set.gamemode run function mcdp_lib:_internal/rules/gm with storage mcdp_lib:internal rules.set
execute if data storage mcdp_lib:internal rules.set{block_break:0b} run attribute @s minecraft:block_break_speed modifier add mcdp_lib:rules_no_break -1 add_multiplied_total
execute if data storage mcdp_lib:internal rules.set.effects[0] run function mcdp_lib:list/foreach {storage:"mcdp_lib:internal",path:"rules.set.effects",function:"mcdp_lib:_internal/rules/effect"}
return 1
