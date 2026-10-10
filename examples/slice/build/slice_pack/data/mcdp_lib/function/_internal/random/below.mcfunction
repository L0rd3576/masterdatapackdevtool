# #r mcdp_lib.var = random in [0, #bound) ; #bound must be >= 1
execute store result score #r mcdp_lib.var run random value 0..2147483646
scoreboard players operation #r mcdp_lib.var %= #bound mcdp_lib.var
