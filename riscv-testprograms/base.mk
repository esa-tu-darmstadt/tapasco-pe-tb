PLATFORM_ARCHFLAGS ?= -march=rv32im -mabi=ilp32
PLATFORM_CFLAGS ?= -T ../platform_link_bram_tapascoriscv.ld ../startup_tapascoriscv.s
STDLIB_FLAG ?= -nostdlib -nostartfiles

CC = riscv32-unknown-elf-gcc
OBJCOPY = riscv32-unknown-elf-objcopy
OBJDUMP = riscv32-unknown-elf-objdump
ifneq ($(origin RISCV_GNU_PREFIX), undefined)
  CC = $(RISCV_GNU_PREFIX)gcc
  OBJCOPY = $(RISCV_GNU_PREFIX)objcopy
  OBJDUMP = $(RISCV_GNU_PREFIX)objdump
endif
ifeq ($(USE_STDLIB),1)
  STDLIB_FLAG :=
endif

BASEFLAGS = $(PLATFORM_ARCHFLAGS) $(STDLIB_FLAG) -g
CFLAGS = $(BASEFLAGS) $(PLATFORM_CFLAGS)
COPYFLAGS = -O binary -j .text.init -j .text -j .data -j .srodata -j .rodata -j .bss -j .sdata 

SRCS = $(wildcard *.c)
ELFS = $(SRCS:%.c=elf/%)
BINS = $(SRCS:%.c=bin/%.bin)

EXECUTABLES = $(ELFS)

ifneq ($(VERBOSE),)
$(info CC=$(CC))
$(info CFLAGS=$(CFLAGS))
$(info OBJDUMP=$(OBJDUMP))
$(info COPYFLAGS=$(COPYFLAGS))
endif

.PHONY: build

all: build

elf/%:
	mkdir -p elf
	$(CC) $(CFLAGS) $*.c $(SRCS_START) -o $@
	$(OBJDUMP) -d $@ > elf/$*_disasm.txt

bin/%.bin: elf/%
	mkdir -p bin
	$(OBJCOPY) $(COPYFLAGS) $< $@

build: $(EXECUTABLES) $(BINS)

clean:
	-rm -f $(wildcard bin/*.bin)
	-rm -f $(EXECUTABLES) $(EXECUTABLES:%=%_disasm.txt)
	
