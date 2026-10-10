data modify storage mcdp_lib_test:o inner set from storage mcdp_lib:out foreach.item
function mcdp_lib:list/foreach {storage:"mcdp_lib_test:o",path:"inner",function:"mcdp_lib_test:cb"}
