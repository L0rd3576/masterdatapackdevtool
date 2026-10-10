$data remove storage mcdp_lib:internal countdowns[{name:"$(name)"}]
$scoreboard players reset #cd.$(name) mcdp_lib.cd
$function $(callback)
