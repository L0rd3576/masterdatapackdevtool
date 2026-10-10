#> mcdp_lib:rules/apply
#> Purpose: Apply a rules struct from mcdp_lib:in rules; remembers previous values so rules/revert can undo it. Any key may be omitted.
#> Inputs: macro {targets:string (entity selector)}; storage mcdp_lib:in rules = {gamemode:"adventure", pvp:0b, keep_inventory:1b, natural_regeneration:1b, fall_damage:0b, block_break:0b, effects:[{id:"minecraft:saturation",duration:"infinite",amplifier:0,hide:1b}]}
#> Outputs: return 1
#> Effects: gamerules pvp/keep_inventory/natural_health_regeneration/fall_damage; game mode (players); block_break:0b adds attribute modifier mcdp_lib:rules_no_break (block_break_speed x0, players only); effects; tag mcdp_lib.ruled. A previous apply is reverted first.
#> Context: any
#> Cost: macro (setup)
#> Example: function mcdp_lib:rules/apply {targets:"@a"}
execute if data storage mcdp_lib:internal rules.active run function mcdp_lib:rules/revert
data modify storage mcdp_lib:internal rules set value {active:1b,prev:{},set:{}}
data modify storage mcdp_lib:internal rules.set set from storage mcdp_lib:in rules
execute if data storage mcdp_lib:in rules.pvp run function mcdp_lib:_internal/rules/gr {rule:"pvp",key:"pvp"}
execute if data storage mcdp_lib:in rules.keep_inventory run function mcdp_lib:_internal/rules/gr {rule:"keep_inventory",key:"keep_inventory"}
execute if data storage mcdp_lib:in rules.natural_regeneration run function mcdp_lib:_internal/rules/gr {rule:"natural_health_regeneration",key:"natural_regeneration"}
execute if data storage mcdp_lib:in rules.fall_damage run function mcdp_lib:_internal/rules/gr {rule:"fall_damage",key:"fall_damage"}
$execute as $(targets) run function mcdp_lib:rules/apply_self
return 1
