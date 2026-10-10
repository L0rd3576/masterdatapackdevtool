$scoreboard players operation #cd.$(name) mcdp_lib.var = #cd.$(name) mcdp_lib.cd
$scoreboard players operation #cd.$(name) mcdp_lib.var /= #20 mcdp_lib.var
$title $(targets) $(display) [{text:"$(label)"},{score:{name:"#cd.$(name)",objective:"mcdp_lib.var"}}]
