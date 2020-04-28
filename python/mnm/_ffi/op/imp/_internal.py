from mnm._lib import _APIS

# pylint: disable=invalid-name,redefined-builtin
# Defined in ./src/op/regs/regs.cc
abs = _APIS.get("mnm.op.imp.abs", None)
# Defined in ./src/op/regs/regs.cc
add = _APIS.get("mnm.op.imp.add", None)
# Defined in ./src/op/regs/regs.cc
avg_pool2d = _APIS.get("mnm.op.imp.avg_pool2d", None)
# Defined in ./src/op/regs/regs.cc
avg_pool2d_dx = _APIS.get("mnm.op.imp.avg_pool2d_dx", None)
# Defined in ./src/op/regs/regs.cc
batch_flatten = _APIS.get("mnm.op.imp.batch_flatten", None)
# Defined in ./src/op/regs/regs.cc
batch_matmul = _APIS.get("mnm.op.imp.batch_matmul", None)
# Defined in ./src/op/regs/regs.cc
batch_norm_infer = _APIS.get("mnm.op.imp.batch_norm_infer", None)
# Defined in ./src/op/regs/regs.cc
batch_norm_train = _APIS.get("mnm.op.imp.batch_norm_train", None)
# Defined in ./src/op/regs/regs.cc
batch_norm_train_dxwb = _APIS.get("mnm.op.imp.batch_norm_train_dxwb", None)
# Defined in ./src/op/regs/regs.cc
broadcast_to = _APIS.get("mnm.op.imp.broadcast_to", None)
# Defined in ./src/op/regs/regs.cc
broadcast_to_like = _APIS.get("mnm.op.imp.broadcast_to_like", None)
# Defined in ./src/op/regs/regs.cc
ceil = _APIS.get("mnm.op.imp.ceil", None)
# Defined in ./src/op/regs/regs.cc
collapse_sum_like = _APIS.get("mnm.op.imp.collapse_sum_like", None)
# Defined in ./src/op/regs/regs.cc
conv2d = _APIS.get("mnm.op.imp.conv2d", None)
# Defined in ./src/op/regs/regs.cc
conv2d_dw = _APIS.get("mnm.op.imp.conv2d_dw", None)
# Defined in ./src/op/regs/regs.cc
conv2d_dx = _APIS.get("mnm.op.imp.conv2d_dx", None)
# Defined in ./src/op/regs/regs.cc
copy = _APIS.get("mnm.op.imp.copy", None)
# Defined in ./src/op/regs/regs.cc
cos = _APIS.get("mnm.op.imp.cos", None)
# Defined in ./src/op/regs/regs.cc
divide = _APIS.get("mnm.op.imp.divide", None)
# Defined in ./src/op/regs/regs.cc
equal = _APIS.get("mnm.op.imp.equal", None)
# Defined in ./src/op/regs/regs.cc
erf = _APIS.get("mnm.op.imp.erf", None)
# Defined in ./src/op/regs/regs.cc
erf_dx = _APIS.get("mnm.op.imp.erf_dx", None)
# Defined in ./src/op/regs/regs.cc
expand_dims = _APIS.get("mnm.op.imp.expand_dims", None)
# Defined in ./src/op/regs/regs.cc
floor = _APIS.get("mnm.op.imp.floor", None)
# Defined in ./src/op/regs/regs.cc
get_kept_dims = _APIS.get("mnm.op.imp.get_kept_dims", None)
# Defined in ./src/op/regs/regs.cc
get_reduce_axis = _APIS.get("mnm.op.imp.get_reduce_axis", None)
# Defined in ./src/op/regs/regs.cc
greater = _APIS.get("mnm.op.imp.greater", None)
# Defined in ./src/op/regs/regs.cc
greater_equal = _APIS.get("mnm.op.imp.greater_equal", None)
# Defined in ./src/op/regs/regs.cc
less = _APIS.get("mnm.op.imp.less", None)
# Defined in ./src/op/regs/regs.cc
less_equal = _APIS.get("mnm.op.imp.less_equal", None)
# Defined in ./src/op/regs/regs.cc
log = _APIS.get("mnm.op.imp.log", None)
# Defined in ./src/op/regs/regs.cc
log_softmax = _APIS.get("mnm.op.imp.log_softmax", None)
# Defined in ./src/op/regs/regs.cc
log_softmax_dx = _APIS.get("mnm.op.imp.log_softmax_dx", None)
# Defined in ./src/op/regs/regs.cc
logical_not = _APIS.get("mnm.op.imp.logical_not", None)
# Defined in ./src/op/regs/regs.cc
matmul = _APIS.get("mnm.op.imp.matmul", None)
# Defined in ./src/op/regs/regs.cc
matmul_nt = _APIS.get("mnm.op.imp.matmul_nt", None)
# Defined in ./src/op/regs/regs.cc
matmul_tn = _APIS.get("mnm.op.imp.matmul_tn", None)
# Defined in ./src/op/regs/regs.cc
matmul_tt = _APIS.get("mnm.op.imp.matmul_tt", None)
# Defined in ./src/op/regs/regs.cc
max_pool2d = _APIS.get("mnm.op.imp.max_pool2d", None)
# Defined in ./src/op/regs/regs.cc
max_pool2d_dx = _APIS.get("mnm.op.imp.max_pool2d_dx", None)
# Defined in ./src/op/regs/regs.cc
maximum = _APIS.get("mnm.op.imp.maximum", None)
# Defined in ./src/op/regs/regs.cc
minimum = _APIS.get("mnm.op.imp.minimum", None)
# Defined in ./src/op/regs/regs.cc
mod = _APIS.get("mnm.op.imp.mod", None)
# Defined in ./src/op/regs/regs.cc
multiply = _APIS.get("mnm.op.imp.multiply", None)
# Defined in ./src/op/regs/regs.cc
negative = _APIS.get("mnm.op.imp.negative", None)
# Defined in ./src/op/regs/regs.cc
nll_loss = _APIS.get("mnm.op.imp.nll_loss", None)
# Defined in ./src/op/regs/regs.cc
nll_loss_dpred = _APIS.get("mnm.op.imp.nll_loss_dpred", None)
# Defined in ./src/op/regs/regs.cc
nll_loss_dtrue = _APIS.get("mnm.op.imp.nll_loss_dtrue", None)
# Defined in ./src/op/regs/regs.cc
not_equal = _APIS.get("mnm.op.imp.not_equal", None)
# Defined in ./src/op/regs/regs.cc
relu = _APIS.get("mnm.op.imp.relu", None)
# Defined in ./src/op/regs/regs.cc
relu_dx = _APIS.get("mnm.op.imp.relu_dx", None)
# Defined in ./src/op/regs/regs.cc
reshape = _APIS.get("mnm.op.imp.reshape", None)
# Defined in ./src/op/regs/regs.cc
sequence_mask = _APIS.get("mnm.op.imp.sequence_mask", None)
# Defined in ./src/op/regs/regs.cc
sgd = _APIS.get("mnm.op.imp.sgd", None)
# Defined in ./src/op/regs/regs.cc
shape = _APIS.get("mnm.op.imp.shape", None)
# Defined in ./src/op/regs/regs.cc
sigmoid = _APIS.get("mnm.op.imp.sigmoid", None)
# Defined in ./src/op/regs/regs.cc
sigmoid_dx = _APIS.get("mnm.op.imp.sigmoid_dx", None)
# Defined in ./src/op/regs/regs.cc
softmax = _APIS.get("mnm.op.imp.softmax", None)
# Defined in ./src/op/regs/regs.cc
softmax_dx = _APIS.get("mnm.op.imp.softmax_dx", None)
# Defined in ./src/op/regs/regs.cc
sqrt = _APIS.get("mnm.op.imp.sqrt", None)
# Defined in ./src/op/regs/regs.cc
sqrt_dx = _APIS.get("mnm.op.imp.sqrt_dx", None)
# Defined in ./src/op/regs/regs.cc
subtract = _APIS.get("mnm.op.imp.subtract", None)
# Defined in ./src/op/regs/regs.cc
sum = _APIS.get("mnm.op.imp.sum", None)
# Defined in ./src/op/regs/regs.cc
take = _APIS.get("mnm.op.imp.take", None)
# Defined in ./src/op/regs/regs.cc
tanh = _APIS.get("mnm.op.imp.tanh", None)
# Defined in ./src/op/regs/regs.cc
tanh_dx = _APIS.get("mnm.op.imp.tanh_dx", None)
# Defined in ./src/op/regs/regs.cc
transpose = _APIS.get("mnm.op.imp.transpose", None)
# Defined in ./src/op/regs/regs.cc
transpose_dx = _APIS.get("mnm.op.imp.transpose_dx", None)
