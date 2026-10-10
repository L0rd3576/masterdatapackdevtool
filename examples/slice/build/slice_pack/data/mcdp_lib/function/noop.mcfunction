#> mcdp_lib:noop
#> Purpose: Does nothing; pass it where a callback is required but none is wanted.
#> Inputs: none
#> Outputs: return 0
#> Effects: none
#> Context: any
#> Cost: fast
#> Example: function mcdp_lib:timer/create {name:"my.cd",callback:"mcdp_lib:noop"}
return 0
