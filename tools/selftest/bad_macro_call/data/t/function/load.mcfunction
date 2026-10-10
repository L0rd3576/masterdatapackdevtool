scoreboard objectives add t dummy
function t:needs_ab {a:1}
execute if function t:needs_ab run say never
