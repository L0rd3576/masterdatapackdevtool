$scoreboard players operation #m mcdp_lib.var = #cd.$(name) mcdp_lib.cd
scoreboard players operation #m mcdp_lib.var %= #20 mcdp_lib.var
$execute if score #m mcdp_lib.var matches 0 if score #cd.$(name) mcdp_lib.cd matches 1.. run function mcdp_lib:_internal/msg/cd_show with storage mcdp_lib:internal cd_scan[0]
$scoreboard players remove #cd.$(name) mcdp_lib.cd 1
$execute if score #cd.$(name) mcdp_lib.cd matches ..0 run function mcdp_lib:_internal/msg/cd_done with storage mcdp_lib:internal cd_scan[0]
