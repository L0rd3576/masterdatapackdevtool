#> slice:round/hook {hook} - run the current minigame's hook function slice:game/<id>/<hook> (keeps @s/position)
$data modify storage slice:tmp hook set value {hook:"$(hook)"}
data modify storage slice:tmp hook.game set from storage slice:round current.game.id
function slice:round/_hook_call with storage slice:tmp hook
