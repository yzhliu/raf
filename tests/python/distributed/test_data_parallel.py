# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=attribute-defined-outside-init,protected-access,too-many-locals
# pylint: disable=too-many-statements,invalid-name
import sys
import pytest

import raf
from raf.model import Conv2d, Linear, BatchNorm
from raf import distributed as dist
from raf.testing import randn, one_hot_torch, run_vm_model, skip_dist_test, with_seed

import tvm


class RAFTest(raf.Model):
    # pylint: disable=attribute-defined-outside-init
    def build(self, input_shape=28, num_classes=10):
        self.conv1 = Conv2d(in_channels=3, out_channels=6, kernel_size=5, padding=2, bias=False)
        self.bn1 = BatchNorm(6)
        self.linear1 = Linear((input_shape // 2) ** 2 * 6, num_classes)

    # pylint: enable=attribute-defined-outside-init

    @raf.model.trace
    def forward(self, x, y_true):
        y_pred = self.forward_infer(x)
        y_pred = raf.log_softmax(y_pred)
        loss = raf.nll_loss(y_true=y_true, y_pred=y_pred)
        return loss

    @raf.model.trace
    def forward_infer(self, x):
        out = self.bn1(self.conv1(x))
        out = raf.sigmoid(out)
        out = raf.avg_pool2d(out, (2, 2), (2, 2))
        out = raf.batch_flatten(out)
        out = self.linear1(out)
        return out


def run_model(device):
    tvm_device = tvm.nd.device("cuda")

    m_model = RAFTest()
    m_model.to(device=device)
    m_model.train_mode()

    m_x, _ = randn([4, 3, 28, 28], device=device, requires_grad=True)
    m_y, _ = one_hot_torch(batch_size=4, num_classes=10, device=device)
    m_dy, _ = randn((), device=device)

    model_train = raf.optim.sgd.with_sgd()(m_model)
    run_vm_model(model_train, device, [m_dy, m_x, m_y])
    tvm_device.sync()


@pytest.mark.skipif(
    skip_dist_test(min_rank_num=2),
    reason="Distribution is not enabled or only one device is available",
)
@with_seed(0)
def test_data_parallel():
    dctx = dist.get_context()
    dctx.enable_data_parallel = True
    device = f"cuda({dctx.local_rank})"

    run_model(device)

    dctx.enable_data_parallel = False


@pytest.mark.skipif(
    skip_dist_test(min_rank_num=2),
    reason="Distribution is not enabled or only one device is available",
)
@with_seed(0)
def test_zero_opt_1():
    dctx = dist.get_context()
    dctx.enable_data_parallel = True
    dctx.zero_opt_level = 1
    device = f"cuda({dctx.local_rank})"

    run_model(device)

    dctx.enable_data_parallel = False
    dctx.zero_opt_level = 0


if __name__ == "__main__":
    exit_code = pytest.main([__file__])
    dist.RemoveCommunicator()
    sys.exit(exit_code)
