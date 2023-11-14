TOPLEVEL_LANG ?= verilog
MODULE ?= tapasco-tests

SIM = questa
MODELSIM = $(PWD)/simulate_testbench.sim/sim_1/behav/questa/modelsim.ini

SIM_LIB = $(PWD)/compile_simlib/questa

SCRIPT_FILE = $(PWD)/simulate_testbench.sim/sim_1/behav/questa/pe_compile.do; \
do $(PWD)/simulate_testbench.sim/sim_1/behav/questa/pe_elaborate.do;

SIM_ARGS=-lib xil_defaultlib pe_opt -suppress 7061 -suppress 12003 -onfinish exit -pli "$(shell cocotb-config --prefix)/cocotb/libs/libcocotbvpi_modelsim.so"; \#
include $(shell cocotb-config --makefiles)/Makefile.sim

RUN_ARGS=-noautoldlibpath
GUI:=0

RTL_LIBRARY = xil_defaultlib
TOPLEVEL := pe

QUESTA_HOME := $(abspath $(dir $(shell which vsim))/../)
ifeq ($(QUESTA_HOME),)
  $(error "Questa installation not detected. Please make sure questa simulator is installed an on PATH")
endif
QUESTA_GCC_LIST := $(wildcard $(QUESTA_HOME)/gcc-1*)
ifeq ($(QUESTA_GCC_LIST),)
QUESTA_GCC_LIST := $(wildcard $(QUESTA_HOME)/gcc-*)
endif
QUESTA_GCC := $(lastword 1, $(sort ${QUESTA_GCC_LIST}))
ifeq ($(QUESTA_GCC),)
  $(error "Questa installation not detected. Please make sure questa simulator is installed an on PATH")
endif

test: sim
	python3 combine_results.py

simlib_questa:
	echo "compile_simlib -simulator questa -simulator_exec_path {$(QUESTA_HOME)/bin} -gcc_exec_path {$(QUESTA_GCC)/bin} -family zynquplus -language all -library all -dir {compile_simlib/questa}" > questa.tcl
	vivado -nojournal -nolog -mode batch -source questa.tcl

clean_viv: clean
	rm -rf user_ip
	rm -rf simulate_testbench.*

vivado_prj: clean_viv
	vivado -source create_sim_verilog.tcl -mode batch
	mkdir simulate_testbench.sim/sim_1/behav/questa/modelsim_lib/
	mkdir sim_build
	cp compile_simlib/questa/modelsim.ini sim_build/
