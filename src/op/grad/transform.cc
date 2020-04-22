/*!
 * Copyright (c) 2019 by Contributors
 * \file src/op/grad/binary.cc
 * \brief Declaration of gradients
 */
#include "./grad_utils.h"

namespace mnm {
namespace op {
namespace grad {

using namespace mnm::ir;

Array<Expr> BatchFlattenGrad(const Expr& orig_call, const Var &y, const Expr& dy) {
  static auto reshape = Op::Get("mnm.op.reshape");
  static auto shape = Op::Get("mnm.op.shape");
  const CallNode* call = orig_call.as<CallNode>();
  return {CallNode::make(reshape, {dy, CallNode::make(shape, {call->args[0]})})};
}

MNM_OP_GRAD("mnm.op.batch_flatten", BatchFlattenGrad);

Array<Expr> TransposeGrad(const Expr& orig_call, const Var &y, const Expr& dy) {
  static auto transpose = Op::Get("mnm.op.transpose");
  const CallNode* call = orig_call.as<CallNode>();
  return {CallNode::make(transpose, {dy, call->args[1]})};
  LOG(FATAL) << "Unreachable code";
  throw;
}

MNM_OP_GRAD("mnm.op.transpose", TransposeGrad);

}  // namespace grad
}  // namespace op
}  // namespace mnm
