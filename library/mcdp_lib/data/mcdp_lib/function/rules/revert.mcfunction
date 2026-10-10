#> mcdp_lib:rules/revert
#> Purpose: Undo rules/apply: restore the previous gamerule values, game modes, attribute and effects.
#> Inputs: none
#> Outputs: return 1, or fail if no rules are active
#> Effects: see rules/apply (effects listed in the struct are cleared)
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:rules/revert
execute unless data storage mcdp_lib:internal rules.active run return fail
execute if data storage mcdp_lib:internal rules.prev.pvp run function mcdp_lib:_internal/rules/gr_revert {rule:"pvp",key:"pvp"}
execute if data storage mcdp_lib:internal rules.prev.keep_inventory run function mcdp_lib:_internal/rules/gr_revert {rule:"keep_inventory",key:"keep_inventory"}
execute if data storage mcdp_lib:internal rules.prev.natural_regeneration run function mcdp_lib:_internal/rules/gr_revert {rule:"natural_health_regeneration",key:"natural_regeneration"}
execute if data storage mcdp_lib:internal rules.prev.fall_damage run function mcdp_lib:_internal/rules/gr_revert {rule:"fall_damage",key:"fall_damage"}
execute as @e[tag=mcdp_lib.ruled] run function mcdp_lib:_internal/rules/revert_entity
data remove storage mcdp_lib:internal rules
return 1
