#> slice:round/_pick {n} - internal: weighted pick from the candidates for n participants
$execute unless data storage slice:registry by_count.n$(n)[0] run return run function slice:round/_no_candidates
$function mcdp_lib:random/weighted {storage:"slice:registry",path:"by_count.n$(n)"}
data modify storage slice:tmp sel.pick set from storage mcdp_lib:out random.value
return run function slice:round/start_with with storage slice:tmp sel.pick
