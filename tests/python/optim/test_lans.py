# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=unused-variable
from unittest.mock import patch
import re
import math
import pytest
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import raf
from raf.model import Conv2d, Linear, BatchNorm
from raf.testing import run_vm_model, one_hot_torch, randn_torch, t2m_param, check, with_seed

try:
    from apex.optimizers import FusedLANS as LANS
except ImportError:
    LANS = None


class TorchTest(nn.Module):  # pylint: disable=abstract-method
    def __init__(self, input_shape=28, num_classes=10):
        super(TorchTest, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5, padding=2, bias=False)
        self.bn1 = nn.BatchNorm2d(6)
        self.linear1 = nn.Linear((input_shape // 2) ** 2 * 6, num_classes)

    def forward(self, x, y_true):  # pylint: disable=arguments-differ
        y_pred = self.forward_infer(x)
        y_pred = F.log_softmax(y_pred, dim=-1)
        loss = F.nll_loss(y_pred, y_true)
        return loss

    def forward_infer(self, x):
        out = self.bn1(self.conv1(x))
        out = torch.sigmoid(out)  # pylint: disable=no-member
        out = F.avg_pool2d(out, (2, 2), (2, 2))
        out = torch.flatten(out, 1)  # pylint: disable=no-member
        out = self.linear1(out)
        return out


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


class TorchSimpleTest(nn.Module):  # pylint: disable=abstract-method
    def __init__(self, shape):
        super(TorchSimpleTest, self).__init__()
        self.x = torch.nn.Parameter(torch.randn(*shape))
        self.x.requires_grad = True

    def forward(self):  # pylint: disable=arguments-differ
        y = F.relu(self.x)
        return y


class RAFSimpleTest(raf.Model):
    # pylint: disable=attribute-defined-outside-init
    def build(self, shape):
        self.x = raf.array(np.random.randn(*shape).astype("float32"))

    @raf.model.trace
    def forward(self):
        y = raf.relu(self.x)
        return y


@with_seed(0)
@pytest.mark.skipif(not raf.build.with_cuda(), reason="CUDA is not enabled")
@pytest.mark.parametrize("config", [(2, 32, 10)])
def test_lans(config):
    t_model = TorchTest(config[1], config[2])
    t_model.to(device="cuda")
    m_model = RAFTest(config[1], config[2])
    m_model.to(device="cuda")
    m_model.conv1.w = t2m_param(t_model.conv1.weight)
    m_model.linear1.w = t2m_param(t_model.linear1.weight)
    m_model.linear1.b = t2m_param(t_model.linear1.bias)
    m_model.bn1.w = t2m_param(t_model.bn1.weight)
    m_model.bn1.b = t2m_param(t_model.bn1.bias)
    m_model.bn1.running_mean = t2m_param(t_model.bn1.running_mean)
    m_model.bn1.running_var = t2m_param(t_model.bn1.running_var)

    m_param_dict = m_model.state()
    m_optimizer = raf.optim.LANS(m_param_dict.values())
    t_optimizer = LANS(t_model.parameters())
    batch_size = config[0]
    m_model.train_mode()
    t_model.train()

    for i in range(batch_size):
        t_optimizer.zero_grad()
        m_x, t_x = randn_torch([1, 3, config[1], config[1]], requires_grad=True, device="cuda")
        m_y, t_y = one_hot_torch(batch_size=1, num_classes=config[2], device="cuda")
        m_loss = m_model(m_x, m_y)
        t_loss = t_model(t_x, t_y)
        m_loss.backward()
        t_loss.backward()
        check(m_model.conv1.w.grad, t_model.conv1.weight.grad, rtol=1e-3, atol=1e-3)
        check(m_model.linear1.w.grad, t_model.linear1.weight.grad, rtol=1e-3, atol=1e-3)
        check(m_model.linear1.b.grad, t_model.linear1.bias.grad, rtol=1e-3, atol=1e-3)
        check(m_model.bn1.w.grad, t_model.bn1.weight.grad, rtol=1e-3, atol=1e-3)
        check(m_model.bn1.b.grad, t_model.bn1.bias.grad, rtol=1e-3, atol=1e-3)
        check(m_loss, t_loss, rtol=1e-3, atol=1e-3)
        m_optimizer.step()
        t_optimizer.step()
        check(m_model.conv1.w, t_model.conv1.weight, rtol=1e-3, atol=1e-3)
        check(m_model.linear1.w, t_model.linear1.weight, rtol=1e-3, atol=1e-3)
        check(m_model.linear1.b, t_model.linear1.bias, rtol=1e-3, atol=1e-3)
        check(m_model.bn1.w, t_model.bn1.weight, rtol=1e-3, atol=1e-3)
        check(m_model.bn1.b, t_model.bn1.bias, rtol=1e-3, atol=1e-3)


@pytest.mark.skipif(not raf.build.with_cuda(), reason="CUDA is not enabled")
def test_traced_lans_simple():
    # pylint: disable=attribute-defined-outside-init
    device = "cuda"
    shape = (2, 2)
    batch_size = 4
    t_model = TorchSimpleTest(shape)
    t_model.train()
    t_model.to(device)
    t_optimizer = LANS(t_model.parameters())
    m_model = RAFSimpleTest(shape)
    m_model.x = t2m_param(t_model.x, device=device)
    m_model.train_mode()
    m_optimizer = raf.optim.lans.with_lans()(m_model)
    for i in range(batch_size):
        m_dy, t_dy = randn_torch(shape, device=device, requires_grad=False)
        m_loss = run_vm_model(m_optimizer, device, [m_dy])
        t_optimizer.zero_grad()
        t_loss = t_model()
        t_loss.backward(t_dy)
        t_optimizer.step()
        check(m_model.x, t_model.x, rtol=1e-4, atol=1e-4)


@with_seed(0)
@pytest.mark.skipif(not raf.build.with_cuda(), reason="CUDA is not enabled")
@pytest.mark.parametrize(
    "config",
    [
        (4, 28, 10),
    ],
)
def test_traced_lans(config):
    # pylint: disable=too-many-locals
    device = "cuda"
    batch_size = config[0]
    t_model = TorchTest(config[1], config[2])
    t_model.to(device=device)
    m_model = RAFTest(config[1], config[2])
    m_model.to(device=device)
    m_model.conv1.w = t2m_param(t_model.conv1.weight, device=device)
    m_model.linear1.w = t2m_param(t_model.linear1.weight, device=device)
    m_model.linear1.b = t2m_param(t_model.linear1.bias, device=device)
    m_model.bn1.w = t2m_param(t_model.bn1.weight, device=device)
    m_model.bn1.b = t2m_param(t_model.bn1.bias, device=device)
    m_model.bn1.running_mean = t2m_param(t_model.bn1.running_mean, device=device)
    m_model.bn1.running_var = t2m_param(t_model.bn1.running_var, device=device)

    m_model.train_mode()
    t_model.train()
    m_optimizer = raf.optim.lans.with_lans()(m_model)
    t_optimizer = LANS(t_model.parameters())
    for i in range(batch_size):
        m_dy, t_dy = randn_torch((), std=0.0, mean=1.0, device=device, requires_grad=False)
        m_x, t_x = randn_torch([1, 3, config[1], config[1]], requires_grad=True, device=device)
        m_y, t_y = one_hot_torch(batch_size=1, num_classes=config[2], device=device)
        m_loss = run_vm_model(m_optimizer, device, [m_dy, m_x, m_y])
        t_optimizer.zero_grad()
        t_loss = t_model(t_x, t_y)
        t_loss.backward(t_dy)
        t_optimizer.step()
        check(m_model.conv1.w, t_model.conv1.weight, rtol=1e-3, atol=1e-3)
        check(m_model.linear1.w, t_model.linear1.weight, rtol=1e-3, atol=1e-3)
        check(m_model.linear1.b, t_model.linear1.bias, rtol=1e-3, atol=1e-3)
        check(m_model.bn1.w, t_model.bn1.weight, rtol=1e-3, atol=1e-3)
        check(m_model.bn1.b, t_model.bn1.bias, rtol=1e-3, atol=1e-3)


@pytest.mark.skipif(not raf.build.with_cuda(), reason="CUDA is not enabled")
@patch("raf.distributed.get_context")
def test_state_partition(mock_get_context):
    """Note that this test only verifies the IR with LANS without checking the correctness.
    Accordingly, this test does not require multiple devices.
    """
    # pylint: disable=too-many-locals, protected-access
    # Mock the context to let with_lans generate the desired IR.
    class MockContext:
        def __init__(self):
            self.enable_data_parallel = True
            self.zero_opt_level = 2
            self.size = 4
            self.rank = 3

    mock_get_context.return_value = MockContext()

    shape, n_classes = 28, 10
    batch_size = 7
    m_model = RAFTest(shape, 10)
    m_model.train_mode()
    m_optimizer = raf.optim.lans.with_lans()(m_model)

    device = "cuda"
    m_x, _ = randn_torch([batch_size, 3, shape, shape], requires_grad=True, device=device)
    m_dy, _ = randn_torch((), std=0.0, mean=1.0, device=device, requires_grad=False)
    m_ytrue, _ = one_hot_torch(batch_size=batch_size, num_classes=n_classes, device=device)
    args = [m_dy, m_x, m_ytrue]

    record = m_optimizer._internal(*args)
    mod = record.mod
    text = raf.ir.AsText(mod)
    # Verify main function arguments.
    func_def = [line for line in text.split("\n") if line.startswith("def @main")]
    assert len(func_def) == 1
    # Extract all tensor arguments and create a {name -> first axis shape} map.
    param_map = {}
    for name, ttype in re.findall(r"%([^:]+): Tensor\[([^\]]+)\]", func_def[0]):
        param_map[name] = int(ttype[ttype.find("(") + 1 : ttype.find(")")].split(",")[0])
    for name, shape in param_map.items():
        if name.find("sgd_") == -1:
            continue
        param_name = f"model.{name[:-6]}"  # Find the original parameter.
        # The size of sgd status should be 1/4 of the original parameter.
        assert param_name in param_map and math.ceil(param_map[param_name] / 4) == shape

    # Verify IR. This model has 7 parameters and 9 gradients
    # (gradients for input data and ytrure are useless).
    assert text.count("raf.op._reduce_scatter") == 9, text
    assert text.count("raf.op._allgather") == 7, text
    assert text.count("raf.op.strided_slice") == 7, text


if __name__ == "__main__":
    pytest.main([__file__])
