data modify storage mcdp_lib:out random.value set from storage mcdp_lib:internal w.list[0].value
scoreboard players operation #result mcdp_lib.out = #idx mcdp_lib.var
return run scoreboard players get #idx mcdp_lib.var
