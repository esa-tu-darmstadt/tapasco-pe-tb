create_project -part xc7z020clg400-1 simulate_testbench -force
exec mkdir -p user_ip
set_property IP_REPO_PATHS [pwd]/user_ip [current_project]
update_ip_catalog
update_ip_catalog -add_ip tapasco_pe.zip -repo_path [pwd]/user_ip
set pe [create_ip -module_name pe -vlnv [get_ipdefs -filter REPOSITORY==[pwd]/user_ip]]
generate_target all $pe

# find top
set_property top [lindex [find_top] 0] [get_filesets sim_1]

set_property target_simulator Questa [current_project]
set_property compxlib.questa_compiled_library_dir {compile_simlib/questa} [current_project]

# Options that will be added to vlog calls in `simulate_testbench.sim/sim_1/behav/questa/pe_compile.do`
# TODO: Make configurable (+initmem+0 required for NaxRiscv)
set_property questa.compile.vlog.more_options "+initmem+0" [get_filesets [current_fileset -simset]]

launch_simulation -scripts_only -absolute_path
