# foreach callback: element {id, duration, amplifier, hide} arrives as macro arguments
$scoreboard players set #h mcdp_lib.var $(hide)
$execute if score #h mcdp_lib.var matches 1 run effect give @s $(id) $(duration) $(amplifier) true
$execute if score #h mcdp_lib.var matches 0 run effect give @s $(id) $(duration) $(amplifier) false
