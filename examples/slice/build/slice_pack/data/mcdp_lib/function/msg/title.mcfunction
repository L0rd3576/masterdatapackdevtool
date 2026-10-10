#> mcdp_lib:msg/title
#> Purpose: Show a title (and optional subtitle) from storage with custom fade times.
#> Inputs: macro {targets:string, fade_in:int, stay:int, fade_out:int (ticks)}; storage mcdp_lib:in title, optional mcdp_lib:in subtitle
#> Outputs: return the number of players reached
#> Effects: title display
#> Context: any
#> Cost: macro
#> Example: function mcdp_lib:msg/title {targets:"@a",fade_in:10,stay:40,fade_out:10}
$title $(targets) times $(fade_in) $(stay) $(fade_out)
$execute if data storage mcdp_lib:in subtitle run title $(targets) subtitle {storage:"mcdp_lib:in",nbt:"subtitle",interpret:true}
$return run title $(targets) title {storage:"mcdp_lib:in",nbt:"title",interpret:true}
