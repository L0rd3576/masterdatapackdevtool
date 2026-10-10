data remove storage mcdp_lib:internal fill_jobs[0]
data modify storage mcdp_lib:internal fj_cb set value {}
data modify storage mcdp_lib:internal fj_cb.fn set from storage mcdp_lib:internal fj.callback
function mcdp_lib:_internal/call with storage mcdp_lib:internal fj_cb
