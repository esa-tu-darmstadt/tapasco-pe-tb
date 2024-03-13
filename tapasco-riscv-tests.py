# Simple testbench for TaPaSCo RISC-V PEs (https://github.com/esa-tu-darmstadt/tapasco-riscv).
# Assumption: PEs are built with 64K+64K instruction and data memory (i.e. BRAM_SIZE=0x10000).
# Uploads a test program onto a RISC-V core, runs it and outputs the result value from the PE controller.
# Does not contain any failure conditions.
#
# Environment variables:
#  TEST - path to a test binary (default: "$(pwd)/../tapasco-riscv/programming/examples/PE/bin/simple_sum.bin")
# Author: Florian Meisel
# Original Author: Carsten Heinz
import struct
import os

import cocotb
from cocotb.binary import BinaryValue
from cocotb.clock import Clock
from cocotb.result import TestFailure, TestSuccess
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotbext.axi import AxiBus, AxiLiteBus, AxiMaster, AxiSlave, AxiRam, AxiLiteMaster, AxiLiteRam, AddressSpace, MemoryRegion
from testbench_util import find_clk, find_rstn, find_axi_s_ctrl, find_axi_s_bram, find_axi_m, axibus_ensure_ids

CLK_PERIOD = 1000

@cocotb.test()
def run_test(dut):
    clk = find_clk(dut)
    cocotb.fork(Clock(clk, CLK_PERIOD).start())

    axim = AxiLiteMaster(AxiLiteBus.from_prefix(dut, find_axi_s_ctrl(dut)), clk)
    axibram_bus = axibus_ensure_ids(AxiBus.from_prefix(dut, find_axi_s_bram(dut)))
    axim_bram = AxiMaster(axibram_bus, clk)
    axis_space = AddressSpace(2**17)
    dram = MemoryRegion(2**17)
    axis_space.register_region(dram, 0x00000)
    axis = AxiSlave(AxiBus.from_prefix(dut, find_axi_m(dut)), clk, target=axis_space)

    #reset
    rst_n = find_rstn(dut)
    rst_n <= 0
    yield Timer(CLK_PERIOD * 10)
    rst_n <= 1
    yield Timer(CLK_PERIOD * 100)
    print("reset done")

    # load firmware
    pwd = os.path.dirname(os.path.realpath(__file__))
    f = open(os.environ['TEST'] if ('TEST' in os.environ) else os.path.join(pwd, "..", "tapasco-riscv", "programming", "examples", "PE", "bin", "simple_sum.bin"), "rb")
    localmem_addr = 0x0000
    while True:
        word = f.read(4)
        if word == b'' or len(word) < 4:
            break
        #print (struct.unpack('BBBB', word))
        yield axim_bram.write(localmem_addr, word)
        localmem_addr += 4
    f.close()

    print ("firmware loaded")

    # start PE
    yield axim.write_dword(0x04, 1) # GIER
    yield axim.write_dword(0x08, 1) # IER
    #yield axim.write_dword(0x20, 0) # arg 0
    yield axim.write_dword(0x30, 3) # arg 1
    yield axim.write_dword(0x40, 4) # arg 2
    #yield axim.write_dword(0x50, 0) # arg 3
    #yield axim.write_dword(0x60, 0) # arg 4
    yield axim.write_dword(0x00, 1) # start

    yield RisingEdge(dut.interrupt)
    print("int received")

    resultLo = yield axim.read_dword(0x10)
    resultHi = yield axim.read_dword(0x14)
    print("result: {}".format(int(resultLo) | (int(resultHi) << 32)))

    if 'GUI' in os.environ and os.environ['GUI'] == '1':
        print("Endless loop to keep GUI alive.")
        while True:
            yield RisingEdge(dut.interrupt)

    dut._log.info("Ok!")

