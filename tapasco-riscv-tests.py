# Simple testbench for TaPaSCo RISC-V PEs (https://github.com/esa-tu-darmstadt/tapasco-riscv).
# Assumption: PEs are built with 64K+64K instruction and data memory (i.e. BRAM_SIZE=0x10000).
# Uploads a test program onto a RISC-V core, runs it and outputs the result value from the PE controller.
# Does not contain any failure conditions.
#
# Environment variables:
#  TEST - path to a test binary (default: "$(pwd)/riscv-testprograms/minimal/bin/main.bin")
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

CLK_PERIOD = 1000

def find_clk(dut):
    dut._discover_all()
    for name in dut._sub_handles:
        if 'clk' in name.lower() and not 'axi' in name.lower():
            return dut._sub_handles[name]
    raise Exception

def find_rstn(dut):
    dut._discover_all()
    for name in dut._sub_handles:
        if ('reset_n' in name.lower() or 'resetn' in name.lower() or 'rst_n' in name.lower() or 'rstn' in name.lower()) and not 'axi' in name.lower():
            return dut._sub_handles[name]
    raise Exception

def find_axi_s_ctrl(dut):
    dut._discover_all()
    for name in dut._sub_handles:
        if 'arvalid' in name.lower() and 's_axi' in name.lower() and not 'bram' in name.lower():
            return '_'.join(name.split('_')[0:-1])

def find_axi_s_bram(dut):
    dut._discover_all()
    for name in dut._sub_handles:
        if 'arvalid' in name.lower() and 's_axi' in name.lower() and 'bram' in name.lower():
            return '_'.join(name.split('_')[0:-1])

def find_axi_m(dut):
    dut._discover_all()
    for name in dut._sub_handles:
        if 'arvalid' in name.lower() and 'm_axi' in name.lower():
            return '_'.join(name.split('_')[0:-1])

class SimFakeObject:
    def __init__(self, n_bits):
        self.value = BinaryValue(n_bits=n_bits)
    def setimmediatevalue(self, v):
        self.value = v
    def __len__(self):
        return self.value.n_bits

@cocotb.test()
def run_test(dut):
    clk = find_clk(dut)
    print(dut._sub_handles)
    cocotb.fork(Clock(clk, CLK_PERIOD).start())

    axim = AxiLiteMaster(AxiLiteBus.from_prefix(dut, find_axi_s_ctrl(dut)), clk)
    axibram_bus = AxiBus.from_prefix(dut, find_axi_s_bram(dut))
    if hasattr(axibram_bus.write.aw, 'awid') and getattr(axibram_bus.write.aw, 'awid') is None:
        # HACK: Work around the 'id' signal requirement of the AXI implementation.
        axibram_bus.write.aw.awid = SimFakeObject(0)
        axibram_bus.write.aw._signals['awid'] = axibram_bus.write.aw.awid
        axibram_bus.write.b.bid = SimFakeObject(0)
        axibram_bus.write.b._signals['bid'] = axibram_bus.write.b.bid
        axibram_bus.read.ar.arid = SimFakeObject(0)
        axibram_bus.read.ar._signals['arid'] = axibram_bus.read.ar.arid
        axibram_bus.read.r.rid = SimFakeObject(0)
        axibram_bus.read.r._signals['rid'] = axibram_bus.read.r.rid
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
    f = open(os.environ['TEST'] if ('TEST' in os.environ) else os.path.join(pwd, "riscv-testprograms", "minimal", "bin", "main.bin"), "rb")
    localmem_addr = 0x0000
    while True:
        word = f.read(4)
        if word == b'' or len(word) < 4:
            break
        print (localmem_addr)
        print (struct.unpack('BBBB', word))
        #word = struct.unpack('i', word)[0]
        yield axim_bram.write(localmem_addr, word)
        localmem_addr += 4
    f.close()

    print ("firmware loaded")

    # start PE
    yield axim.write_dword(0x04, 1) # GIER
    yield axim.write_dword(0x08, 1) # IER
    #yield axim.write_dword(0x20, 0) # arg 0
    #yield axim.write_dword(0x30, 0) # arg 1
    #yield axim.write_dword(0x40, 0) # arg 2
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

