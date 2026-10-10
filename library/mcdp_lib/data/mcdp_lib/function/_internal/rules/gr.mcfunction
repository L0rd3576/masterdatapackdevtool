$execute store result storage mcdp_lib:internal rules.prev.$(key) byte 1 run gamerule $(rule)
$execute if data storage mcdp_lib:in rules{$(key):1b} run gamerule $(rule) true
$execute if data storage mcdp_lib:in rules{$(key):0b} run gamerule $(rule) false
