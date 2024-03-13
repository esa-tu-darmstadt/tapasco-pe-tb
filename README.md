TaPaSCo PE Testbench
--------------------

This project aims to make the simulation of processing elements (PEs) for [TaPaSCo](https://github.com/esa-tu-darmstadt/tapasco) easier. The testbench uses [cocotb](https://github.com/cocotb/cocotb), but extends it to better support IP-XACT cores and Xilinx simulation primitives.

## Requirements

* Vivado
* Questa Simulator

## Simulation

* Add your IP as tapasco_pe.zip into the main directory
* define your testcase(s) in `tapasco-tests.py`

Setup simulation:
```bash
pip3 install --user cocotb-bus cocotbext-axi
# ensure that cocotb-config is on path
# build xilinx IP for simulation:
make simlib_questa
# create simulator scripts for the PE:
make vivado_prj
```

Then run the simulation:
```bash
MODULE=tapasco-tests make
```

Note: Some changes require a `make clean`

GUI can be enabled by setting the value in the Makefile to 1.

For [TaPaSCo RISC-V](https://github.com/esa-tu-darmstadt/tapasco-riscv) PEs, the `tapasco-riscv-tests` module can be used. For a simple build environment for compatible RISC-V binaries, see [`programming/examples/PE`](https://github.com/esa-tu-darmstadt/tapasco-riscv/tree/master/programming/examples/PE) in the TaPaSCo RISC-V repository.

_If there are any problems, use `.gitlab-ci.yml` as a guideline._

## Debugging the Python side of things (in VS Code)
1. Add the following to your Python test module (the one you name in the Makefile).
```python
import debugpy
debugpy.listen(5678)
print("Waiting for debugger attach")
debugpy.wait_for_client()
```
You can also explicitly name your host and the port number (``5678`` is the VS Code default) in the call to ``debugpy.listen``. When you run ``make`` and launch the simulator, the execution will hang due to the ``debugpy.wait_for_client()``. This is the chance you have been waiting for. Grab it by hopping into VS Code and continuing with the next step.

2. Create a launch configuration. For this, go to the ``RUN AND DEBUG`` view. If you don't already have a ``launch.json``, VS Code will propose to create one for you. When prompted for the type of debugging, choose ``Python`` -> ``Remote Attach`` and enter your host configuration. If you are running locally, you can just use the ``localhost 5678`` configuration that you obtain by just pressing ``Enter`` until VS Code stops bothering you. Just make sure that the port you enter matches the port specified in step (1). Also get rid of the path mappings, as you don't need them when debugging locally and they will lead to failing breakpoint creation.
   
3. Launch the debugger and connect to your running simulation. You can then navigate the VS Code visual debugger like you are used to and set breakpoints. You can also set breakpoints programmatically by placing ``debugpy.breakpoint()`` calls in your testbench code.

4. Note that you have to kill the simulation process in your terminal with ``CTRL + C`` and detach the VS Code debugger separately.
