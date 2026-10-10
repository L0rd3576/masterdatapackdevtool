#> __ns__:round/_no_candidates - internal: nothing fits the queued participant count
data modify storage __ns__:round last_error set value "no minigame/map fits the participant count"
tellraw @a[tag=__ns__.queued] [{text:"No minigame fits ",color:"red"},{score:{name:"#n",objective:"__ns__.round"}},{text:" participants."}]
return fail
