$data modify storage mcdp_lib:internal sh.dst append from storage mcdp_lib:internal sh.src[$(i)]
$data remove storage mcdp_lib:internal sh.src[$(i)]
