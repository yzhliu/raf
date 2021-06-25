/*!
 * \file src/impl/vm/vm_profiler.h
 * \brief The Relay debug virtual machine.
 */

#pragma once

#include "mnm/vm/vm.h"

#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

namespace mnm {
namespace executor {
namespace vm {

class VirtualMachineProfiler : public VirtualMachine {
 public:
  VirtualMachineProfiler(bool enable_cuda_graph, bool cache_interm_tensors)
      : VirtualMachine(enable_cuda_graph), cache_interm_tensors_(cache_interm_tensors) {
  }

  PackedFunc GetFunction(const std::string& name, const ObjectPtr<Object>& sptr_to_self) final;

  ~VirtualMachineProfiler() {
  }

 protected:
  void ExecuteOpEnv(OpEnv* op_env, const std::vector<value::Value>& inputs,
                    value::Value output) final;

 private:
  /*! \brief the duration of op call */
  std::unordered_map<OpEnv*, std::vector<double>> op_durations_;
  /*! \brief the input and output shape string of op call */
  std::unordered_map<OpEnv*, std::string> op_shapes_;
  /*! \brief the number of times of op call */
  std::unordered_map<OpEnv*, int> op_invokes_;
  /*! \brief whether to cache intermediate tensors */
  bool cache_interm_tensors_;
  /*! \brief all op envs sorted in invoke order */
  Array<String> op_names_;
  /*! \brief the inputs for op_envs_ */
  Array<Array<Value>> op_inputs_;
  /*! \brief the outputs for op_envs_ */
  Array<Value> op_outputs_;
  /*! \brief whether to run memory profiling mode */
  bool profile_memory_ = false;
  /*! \brief The number of performed garbage collections for each device memory pool. */
  std::vector<size_t> num_gcs_;
  /*! \brief The peak of used memory and total allocated memory of each device memory pool */
  std::vector<std::pair<float, float>> peak_memory_mbs_;
  /*! \brief the memory trace that maps the executed op to peak memory of each device */
  std::vector<std::pair<OpEnv*, std::vector<std::pair<float, float>>>> memory_trace_;
};

}  // namespace vm
}  // namespace executor
}  // namespace mnm
