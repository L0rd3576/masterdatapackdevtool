#> mcdp_lib:player/count
#> Purpose: Count entities/players matching a selector (e.g. "@a[team=red]", "@a[tag=alive]").
#> Inputs: macro {selector:string}
#> Outputs: score #result mcdp_lib.out; return the count
#> Effects: none
#> Context: any (relative selectors use the current position)
#> Cost: macro; hot path: execute store result score X if entity <selector>
#> Example: execute store result score #alive my.game run function mcdp_lib:player/count {selector:"@a[tag=my.alive]"}
$execute store result score #result mcdp_lib.out if entity $(selector)
return run scoreboard players get #result mcdp_lib.out
