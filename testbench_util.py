# Testbench utility functions

from cocotb.binary import BinaryValue
from cocotbext.axi import AxiBus, AxiLiteBus, AxiMaster, AxiLiteMaster, AxiLiteRam

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
    raise Exception

def find_axi_s_bram(dut):
    dut._discover_all()
    for name in dut._sub_handles:
        if 'arvalid' in name.lower() and 's_axi' in name.lower() and 'bram' in name.lower():
            return '_'.join(name.split('_')[0:-1])
    raise Exception

def find_axi_m(dut):
    dut._discover_all()
    for name in dut._sub_handles:
        if 'arvalid' in name.lower() and 'm_axi' in name.lower():
            return '_'.join(name.split('_')[0:-1])
    raise Exception

class SimFakeObject:
    def __init__(self, n_bits):
        self.value = BinaryValue(n_bits=n_bits)
    def setimmediatevalue(self, v):
        self.value = v
    def __len__(self):
        return self.value.n_bits

def axibus_ensure_ids(axibus: AxiBus) -> AxiBus:
    """Works around the 'id' signal requirement of the AXI implementation.
    
    If the AXI id pins are missing from the given bus, adds fake 0-bit signals,
    as the simulator-side AXI implementation may require something to be present.
    Returns axibus.
    """
    if hasattr(axibus.write.aw, 'awid') and getattr(axibus.write.aw, 'awid') is None:
        # HACK: Work around the 'id' signal requirement of the AXI implementation.
        axibus.write.aw.awid = SimFakeObject(0)
        axibus.write.aw._signals['awid'] = axibus.write.aw.awid
        axibus.write.b.bid = SimFakeObject(0)
        axibus.write.b._signals['bid'] = axibus.write.b.bid
        axibus.read.ar.arid = SimFakeObject(0)
        axibus.read.ar._signals['arid'] = axibus.read.ar.arid
        axibus.read.r.rid = SimFakeObject(0)
        axibus.read.r._signals['rid'] = axibus.read.r.rid
    return axibus
