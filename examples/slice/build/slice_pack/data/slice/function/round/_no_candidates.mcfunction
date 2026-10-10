#> slice:round/_no_candidates - internal: nothing fits the queued participant count
data modify storage slice:round last_error set value "no minigame/map fits the participant count"
tellraw @a[tag=slice.queued] [{text:"No minigame fits ",color:"red"},{score:{name:"#n",objective:"slice.round"}},{text:" participants."}]
return fail
