$data modify storage mcdp_lib:internal cur set value {uuid:$(uuid)}
$data modify storage mcdp_lib:internal cur set from storage mcdp_lib:internal saved[{uuid:$(uuid)}]
$data remove storage mcdp_lib:internal saved[{uuid:$(uuid)}]
