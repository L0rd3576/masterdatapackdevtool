#> mcdp_lib:msg/tell
#> Purpose: Send the text component stored in mcdp_lib:in text to the selected players.
#> Inputs: macro {targets:string (player selector)}; text component in storage mcdp_lib:in text
#> Outputs: return the number of players reached
#> Effects: chat message
#> Context: any (selectors in the text resolve against the executor)
#> Cost: macro
#> Example: data modify storage mcdp_lib:in text set value {text:"Round over",color:"gold"}
$return run tellraw $(targets) {storage:"mcdp_lib:in",nbt:"text",interpret:true}
