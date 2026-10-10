#> __ns__:round/_win_check {win} - internal: end the round when the win condition's check succeeds
$execute if function __ns__:win/$(win)/check run function __ns__:round/end
