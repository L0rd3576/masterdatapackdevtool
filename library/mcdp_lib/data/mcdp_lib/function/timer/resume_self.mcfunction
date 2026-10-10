#> mcdp_lib:timer/resume_self
#> Purpose: Resume @s's instance of a timer paused with pause_self.
#> Inputs: macro {name:string}
#> Outputs: return 1
#> Effects: removes tag mcdp_lib.paused.<name> from @s
#> Context: as an entity (@s)
#> Cost: macro
#> Example: execute as @p run function mcdp_lib:timer/resume_self {name:"my.dash_cd"}
$tag @s remove mcdp_lib.paused.$(name)
return 1
