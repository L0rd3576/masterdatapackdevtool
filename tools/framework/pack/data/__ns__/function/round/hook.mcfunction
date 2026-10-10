#> __ns__:round/hook {hook} - run the current minigame's hook function __ns__:game/<id>/<hook> (keeps @s/position)
$data modify storage __ns__:tmp hook set value {hook:"$(hook)"}
data modify storage __ns__:tmp hook.game set from storage __ns__:round current.game.id
function __ns__:round/_hook_call with storage __ns__:tmp hook
