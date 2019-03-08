#include <mnm/memory_pool.h>
#include <mnm/registry.h>
#include "./commons.h"

namespace mnm {
namespace memory_pool {

using mnm::device_api::DeviceAPI;
using mnm::device_api::DeviceAPIManager;
using mnm::registry::Registry;
using mnm::types::Context;
using mnm::types::DataType;
using mnm::types::DeviceType;
using PoolPtr = std::unique_ptr<MemoryPool>;

MemoryPool* MemoryPool::Create(const char* name) {
  static const std::string prefix("mnm.memory_pool.");
  std::string creator_name = prefix + name;
  auto creator = Registry::Get(creator_name);
  CHECK(creator != nullptr) << "ValueError: MemoryPool " << creator_name << " is not enabled.";
  void* ret = (*creator)();
  return static_cast<MemoryPool*>(ret);
}

inline const char* GetDefaultPool(DeviceType device_type) {
  switch (device_type) {
    case DeviceType::kDLCPU:
      return "no_pool";
    default:
      LOG(FATAL) << "InternalError: Default memory pool is not defined for " << device_type;
  }
  return nullptr;
}

class MemoryPoolManager::Impl {
 public:
  static inline void SetMemoryPool(MemoryPoolManager* self, MemoryPool* pool, Context ctx) {
    DeviceAPI* api = self->device_api_manager_->GetAPI(ctx.device_type, false);
    CHECK(api != nullptr) << "InternalError: device api does not exist";
    int device_id = ctx.device_id;
    pool->ctx_hint_ = ctx;
    pool->f_alloc_ = [api, device_id](size_t nbytes, size_t alignment, DataType type_hint) {
      return api->AllocMemory(device_id, nbytes, alignment, type_hint);
    };
    pool->f_dealloc_ = [api, device_id](void* ptr) { api->DeallocMemory(device_id, ptr); };
  }

  static inline PoolPtr& GetPoolPtr(MemoryPoolManager* self, Context ctx, const char* name,
                                    bool create_if_missing) {
    int device_type = int(ctx.device_type);
    int device_id = ctx.device_id;
    std::vector<PoolPtr>& pool_vec = self->pools_[device_type];
    LOCKED_IF(pool_vec.empty(), self->mutex_, {
      DeviceAPI* api = self->device_api_manager_->GetAPI(ctx.device_type, false);
      int n_devices = api->GetNDevices();
      CHECK_LT(device_id, n_devices) << "ValueError: Device " << device_id << " not found.";
      pool_vec.resize(n_devices);
    });
    int n_devices = pool_vec.size();
    CHECK_LT(device_id, n_devices) << "ValueError: Device " << device_id << " not found.";
    PoolPtr& ptr = pool_vec[device_id];
    LOCKED_IF(create_if_missing && ptr == nullptr, self->mutex_, {
      if (name == nullptr) {
        name = GetDefaultPool(ctx.device_type);
      }
      ptr.reset(MemoryPool::Create(name));
      MemoryPoolManager::Impl::SetMemoryPool(self, ptr.get(), ctx);
    });
    return ptr;
  }
};

MemoryPoolManager::~MemoryPoolManager() {
  for (std::vector<PoolPtr>& pools : pools_) {
    for (PoolPtr& pool : pools) {
      pool->DeallocAll();
      pool = nullptr;
    }
  }
  device_api_manager_ = nullptr;
}

MemoryPool* MemoryPoolManager::Replace(Context ctx, const char* name) {
  PoolPtr& ptr = Impl::GetPoolPtr(this, ctx, name, false);
  std::lock_guard<std::mutex> lock(mutex_);
  if (ptr != nullptr) {
    ptr->DeallocAll();
    ptr = nullptr;
  }
  ptr.reset(MemoryPool::Create(name));
  return ptr.get();
}

MemoryChunk* MemoryPoolManager::Alloc(Context ctx, size_t nbytes, size_t alignment,
                                      DataType type_hint) {
  return Impl::GetPoolPtr(this, ctx, nullptr, true)->Alloc(nbytes, alignment, type_hint);
}

void MemoryPoolManager::Dealloc(Context ctx, MemoryChunk* mem) {
  return Impl::GetPoolPtr(this, ctx, nullptr, false)->Dealloc(mem);
}

}  // namespace memory_pool
}  // namespace mnm
