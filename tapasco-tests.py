import struct
import os

import cocotb
from cocotb.clock import Clock
from cocotb.result import TestFailure, TestSuccess
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotbext.axi import AxiBus, AxiLiteBus, AxiMaster, AxiLiteMaster, AxiLiteRam
from testbench_util import find_clk, find_rstn, find_axi_s_ctrl

CLK_PERIOD = 1000

@cocotb.test()
def run_test(dut):
    clk = find_clk(dut)
    cocotb.fork(Clock(clk, CLK_PERIOD).start())

    # Connect AXI control interface
    axim = AxiLiteMaster(AxiLiteBus.from_prefix(dut, find_axi_s_ctrl(dut)), clk)

    #reset
    rst_n = find_rstn(dut)
    rst_n.value = 0
    yield Timer(CLK_PERIOD * 10)
    rst_n.value = 1
    yield Timer(CLK_PERIOD * 100)
    print("reset done")

    # PE register map
    # 0x00 control (start, GIER, IER)
    # 0x10 result
    # 0x20 argument 0
    # 0x30 argument 1
    # ...

    # start PE
    yield(axim.read(0x00, 4))
    yield axim.write(0x04, (1).to_bytes(4, byteorder = 'little')) # GIER
    yield axim.write(0x08, (1).to_bytes(4, byteorder = 'little')) # IER
    yield axim.write(0x20, (10000).to_bytes(8, byteorder = 'little')) # arg 0, count 1000 cycles
    yield axim.write(0x00, (1).to_bytes(4, byteorder = 'little')) # start

    yield RisingEdge(dut.interrupt)
    print("interrupt received")

    result = yield axim.read(0x10, 4)
    print("result: {}".format(int.from_bytes(result.data, byteorder='little')))

    dut._log.info("Ok!")
