#> slice:round/_win_check {win} - internal: end the round when the win condition's check succeeds
$execute if function slice:win/$(win)/check run function slice:round/end
