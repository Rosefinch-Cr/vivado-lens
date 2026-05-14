# Arty A7-35T pin constraints (xc7a35tcsg324-1)
# 100 MHz system clock
create_clock -period 10.000 -name sys_clk [get_ports clk]

set_property -dict {PACKAGE_PIN E3 IOSTANDARD LVCMOS33} [get_ports clk]
set_property -dict {PACKAGE_PIN C2 IOSTANDARD LVCMOS33} [get_ports rst_n]

# Switches a[7:0]
set_property -dict {PACKAGE_PIN A8  IOSTANDARD LVCMOS33} [get_ports {a[0]}]
set_property -dict {PACKAGE_PIN C11 IOSTANDARD LVCMOS33} [get_ports {a[1]}]
set_property -dict {PACKAGE_PIN C10 IOSTANDARD LVCMOS33} [get_ports {a[2]}]
set_property -dict {PACKAGE_PIN A10 IOSTANDARD LVCMOS33} [get_ports {a[3]}]
set_property -dict {PACKAGE_PIN A15 IOSTANDARD LVCMOS33} [get_ports {a[4]}]
set_property -dict {PACKAGE_PIN B15 IOSTANDARD LVCMOS33} [get_ports {a[5]}]
set_property -dict {PACKAGE_PIN A17 IOSTANDARD LVCMOS33} [get_ports {a[6]}]
set_property -dict {PACKAGE_PIN B17 IOSTANDARD LVCMOS33} [get_ports {a[7]}]

# Buttons b[7:0] (limited; reuse switches for demo via different pins on a real board)
set_property -dict {PACKAGE_PIN D9  IOSTANDARD LVCMOS33} [get_ports {b[0]}]
set_property -dict {PACKAGE_PIN C9  IOSTANDARD LVCMOS33} [get_ports {b[1]}]
set_property -dict {PACKAGE_PIN B9  IOSTANDARD LVCMOS33} [get_ports {b[2]}]
set_property -dict {PACKAGE_PIN B8  IOSTANDARD LVCMOS33} [get_ports {b[3]}]
set_property -dict {PACKAGE_PIN H17 IOSTANDARD LVCMOS33} [get_ports {b[4]}]
set_property -dict {PACKAGE_PIN K15 IOSTANDARD LVCMOS33} [get_ports {b[5]}]
set_property -dict {PACKAGE_PIN J13 IOSTANDARD LVCMOS33} [get_ports {b[6]}]
set_property -dict {PACKAGE_PIN N14 IOSTANDARD LVCMOS33} [get_ports {b[7]}]

# Op select op[2:0]
set_property -dict {PACKAGE_PIN R11 IOSTANDARD LVCMOS33} [get_ports {op[0]}]
set_property -dict {PACKAGE_PIN R12 IOSTANDARD LVCMOS33} [get_ports {op[1]}]
set_property -dict {PACKAGE_PIN R13 IOSTANDARD LVCMOS33} [get_ports {op[2]}]

# Result LEDs
set_property -dict {PACKAGE_PIN H5  IOSTANDARD LVCMOS33} [get_ports {result[0]}]
set_property -dict {PACKAGE_PIN J5  IOSTANDARD LVCMOS33} [get_ports {result[1]}]
set_property -dict {PACKAGE_PIN T9  IOSTANDARD LVCMOS33} [get_ports {result[2]}]
set_property -dict {PACKAGE_PIN T10 IOSTANDARD LVCMOS33} [get_ports {result[3]}]
set_property -dict {PACKAGE_PIN G6  IOSTANDARD LVCMOS33} [get_ports {result[4]}]
set_property -dict {PACKAGE_PIN F6  IOSTANDARD LVCMOS33} [get_ports {result[5]}]
set_property -dict {PACKAGE_PIN J4  IOSTANDARD LVCMOS33} [get_ports {result[6]}]
set_property -dict {PACKAGE_PIN J2  IOSTANDARD LVCMOS33} [get_ports {result[7]}]

# Flag LEDs
set_property -dict {PACKAGE_PIN H6 IOSTANDARD LVCMOS33} [get_ports zero]
set_property -dict {PACKAGE_PIN K1 IOSTANDARD LVCMOS33} [get_ports negative]
set_property -dict {PACKAGE_PIN H1 IOSTANDARD LVCMOS33} [get_ports carry]
