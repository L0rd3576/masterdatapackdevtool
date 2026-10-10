$data modify entity @n[type=minecraft:item_display,tag=mcdp_lib.scratch] item set from storage mcdp_lib:internal cur.eq.$(key)
$item replace entity @s $(slot) from entity @n[type=minecraft:item_display,tag=mcdp_lib.scratch] contents
