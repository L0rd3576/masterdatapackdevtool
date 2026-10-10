#> __ns__:round/_pick {n} - internal: weighted pick from the candidates for n participants
$execute unless data storage __ns__:registry by_count.n$(n)[0] run return run function __ns__:round/_no_candidates
$function __lib__:random/weighted {storage:"__ns__:registry",path:"by_count.n$(n)"}
data modify storage __ns__:tmp sel.pick set from storage __lib__:out random.value
return run function __ns__:round/start_with with storage __ns__:tmp sel.pick
