#> pvp_arena player_start hook: as/at each participant. __ns__ is replaced with the pack namespace at build time.
#> Hands out the weapon chosen by setting `kit` (players only; test stand-ins are armor stands).
execute if data storage __ns__:round current.settings{kit:"sword"} run give @s[type=minecraft:player] minecraft:iron_sword
execute if data storage __ns__:round current.settings{kit:"axe"} run give @s[type=minecraft:player] minecraft:iron_axe
