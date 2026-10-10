#> mcdp_lib:msg/actionbar
#> Purpose: Show the text component in mcdp_lib:in text on the action bar.
#> Inputs: macro {targets:string}; storage mcdp_lib:in text
#> Outputs: return the number of players reached
#> Effects: action bar display
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:msg/actionbar {targets:"@a[team=my.red]"}
$return run title $(targets) actionbar {storage:"mcdp_lib:in",nbt:"text",interpret:true}
