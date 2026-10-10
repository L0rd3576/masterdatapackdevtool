$execute if data storage mcdp_lib:internal rules.prev{$(key):1b} run gamerule $(rule) true
$execute if data storage mcdp_lib:internal rules.prev{$(key):0b} run gamerule $(rule) false
