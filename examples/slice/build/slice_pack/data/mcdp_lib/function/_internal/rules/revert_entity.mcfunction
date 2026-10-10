tag @s remove mcdp_lib.ruled
execute if entity @s[type=minecraft:player] if data storage mcdp_lib:internal rules.set.gamemode run function mcdp_lib:player/restore_gamemode
execute if data storage mcdp_lib:internal rules.set{block_break:0b} run attribute @s minecraft:block_break_speed modifier remove mcdp_lib:rules_no_break
execute if data storage mcdp_lib:internal rules.set.effects[0] run function mcdp_lib:list/foreach {storage:"mcdp_lib:internal",path:"rules.set.effects",function:"mcdp_lib:_internal/rules/uneffect"}
