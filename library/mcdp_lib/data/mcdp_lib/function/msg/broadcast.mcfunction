#> mcdp_lib:msg/broadcast
#> Purpose: Send the text component in mcdp_lib:in text to every player.
#> Inputs: text component in storage mcdp_lib:in text
#> Outputs: return the number of players reached
#> Effects: chat message
#> Context: any
#> Cost: fast (no macro)
#> Example: function mcdp_lib:msg/broadcast
return run tellraw @a {storage:"mcdp_lib:in",nbt:"text",interpret:true}
