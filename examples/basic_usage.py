#!/usr/bin/env python3
"""
Basic usage examples for IPLM with hierarchical IP structure
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import Process, IP, Type, ip_manager, db_manager

def main():
    """Basic usage examples with hierarchical IP structure"""
    print("IPLM Hierarchical IP Management Examples")
    print("=" * 50)
    
    # Initialize database
    print("1. Initializing database...")
    if not db_manager.connect():
        print("Failed to connect to database. Please check your MySQL configuration.")
        return
    
    db_manager.create_tables()
    print("Database initialized successfully!")
    
    # Create types (tree structure)
    print("\n2. Creating type hierarchy...")
    
    # Root types
    digital_type = Type(name="Digital", description="Digital IP types")
    analog_type = Type(name="Analog", description="Analog IP types")
    mixed_signal_type = Type(name="Mixed-Signal", description="Mixed-signal IP types")
    digital_type.save()
    analog_type.save()
    mixed_signal_type.save()
    
    # Digital subtypes
    processor_type = Type(name="Processor", parent_id=digital_type.id, description="Processor cores")
    memory_type = Type(name="Memory", parent_id=digital_type.id, description="Memory controllers")
    interface_type = Type(name="Interface", parent_id=digital_type.id, description="Communication interfaces")
    peripheral_type = Type(name="Peripheral", parent_id=digital_type.id, description="System peripherals")
    
    processor_type.save()
    memory_type.save()
    interface_type.save()
    peripheral_type.save()
    
    # Processor subtypes
    riscv_type = Type(name="RISC-V", parent_id=processor_type.id, description="RISC-V processor cores")
    arm_type = Type(name="ARM", parent_id=processor_type.id, description="ARM processor cores")
    
    riscv_type.save()
    arm_type.save()
    
    # Memory subtypes
    ddr_type = Type(name="DDR", parent_id=memory_type.id, description="DDR memory controllers")
    sram_type = Type(name="SRAM", parent_id=memory_type.id, description="SRAM controllers")
    
    ddr_type.save()
    sram_type.save()
    
    # Interface subtypes
    pcie_type = Type(name="PCIe", parent_id=interface_type.id, description="PCIe interfaces")
    usb_type = Type(name="USB", parent_id=interface_type.id, description="USB interfaces")
    ethernet_type = Type(name="Ethernet", parent_id=interface_type.id, description="Ethernet interfaces")
    
    pcie_type.save()
    usb_type.save()
    ethernet_type.save()
    
    # Peripheral subtypes
    uart_type = Type(name="UART", parent_id=peripheral_type.id, description="UART controllers")
    gpio_type = Type(name="GPIO", parent_id=peripheral_type.id, description="GPIO controllers")
    timer_type = Type(name="Timer", parent_id=peripheral_type.id, description="Timer controllers")
    
    uart_type.save()
    gpio_type.save()
    timer_type.save()
    
    # Analog subtypes
    adc_type = Type(name="ADC", parent_id=analog_type.id, description="Analog-to-Digital converters")
    dac_type = Type(name="DAC", parent_id=analog_type.id, description="Digital-to-Analog converters")
    
    adc_type.save()
    dac_type.save()
    
    print("Type hierarchy created:")
    print_type_tree()
    
    # Create TSMC process
    print("\n3. Creating TSMC process...")
    
    tsmc_process = Process(
        name="TSMC_7nm_SoC_Design",
        node="7nm",
        fab="TSMC",
        description="TSMC 7nm SoC design process for high-performance applications"
    )
    tsmc_process.save()
    
    print(f"Process created: {tsmc_process.name} (Node: {tsmc_process.node}, FAB: {tsmc_process.fab})")
    
    # Create hierarchical IP structure
    print("\n4. Creating hierarchical IP structure...")
    
    # Top-level SoC
    soc_ip = IP(
        name="TSMC_7nm_SoC_v1.0",
        type_id=digital_type.id,  # SoC is a digital type
        process_id=tsmc_process.id,
        revision="1.0",
        status="production",
        provider="TSMC",
        description="Complete 7nm SoC with multiple processing units and interfaces"
    )
    soc_ip.save()
    
    # CPU Subsystem
    cpu_subsystem = IP(
        name="CPU_Subsystem",
        type_id=processor_type.id,
        process_id=tsmc_process.id,
        revision="2.1",
        status="production",
        provider="TSMC",
        description="CPU subsystem containing multiple processor cores"
    )
    cpu_subsystem.save()
    soc_ip.add_child(cpu_subsystem)
    
    # RISC-V cores in CPU subsystem
    riscv_core1 = IP(
        name="RISC-V_RV64GC_2GHz",
        type_id=riscv_type.id,
        process_id=tsmc_process.id,
        revision="1.2",
        status="production",
        provider="SiFive",
        description="High-performance RISC-V RV64GC core at 2GHz"
    )
    riscv_core1.save()
    cpu_subsystem.add_child(riscv_core1)
    
    riscv_core2 = IP(
        name="RISC-V_RV64GC_1.5GHz",
        type_id=riscv_type.id,
        process_id=tsmc_process.id,
        revision="1.2",
        status="production",
        provider="SiFive",
        description="Power-efficient RISC-V RV64GC core at 1.5GHz"
    )
    riscv_core2.save()
    cpu_subsystem.add_child(riscv_core2)
    
    # ARM core in CPU subsystem
    arm_core = IP(
        name="ARM_Cortex-A78_2.5GHz",
        type_id=arm_type.id,
        process_id=tsmc_process.id,
        revision="2.1",
        status="production",
        provider="ARM Ltd.",
        description="High-performance ARM Cortex-A78 core at 2.5GHz"
    )
    arm_core.save()
    cpu_subsystem.add_child(arm_core)
    
    # Memory Subsystem
    memory_subsystem = IP(
        name="Memory_Subsystem",
        type_id=memory_type.id,
        process_id=tsmc_process.id,
        revision="3.0",
        status="production",
        provider="TSMC",
        description="Memory subsystem with DDR and SRAM controllers"
    )
    memory_subsystem.save()
    soc_ip.add_child(memory_subsystem)
    
    # DDR controllers
    ddr4_controller = IP(
        name="DDR4_Controller_3200MHz",
        type_id=ddr_type.id,
        process_id=tsmc_process.id,
        revision="4.1",
        status="production",
        provider="Synopsys",
        description="DDR4 memory controller supporting up to 3200MHz"
    )
    ddr4_controller.save()
    memory_subsystem.add_child(ddr4_controller)
    
    # SRAM controllers
    sram_controller1 = IP(
        name="L1_SRAM_Controller_32KB",
        type_id=sram_type.id,
        process_id=tsmc_process.id,
        revision="2.0",
        status="production",
        provider="TSMC",
        description="L1 SRAM controller for 32KB cache"
    )
    sram_controller1.save()
    memory_subsystem.add_child(sram_controller1)
    
    sram_controller2 = IP(
        name="L2_SRAM_Controller_256KB",
        type_id=sram_type.id,
        process_id=tsmc_process.id,
        revision="2.0",
        status="production",
        provider="TSMC",
        description="L2 SRAM controller for 256KB cache"
    )
    sram_controller2.save()
    memory_subsystem.add_child(sram_controller2)
    
    # Interface Subsystem
    interface_subsystem = IP(
        name="Interface_Subsystem",
        type_id=interface_type.id,
        process_id=tsmc_process.id,
        revision="1.5",
        status="production",
        provider="TSMC",
        description="Interface subsystem with various communication protocols"
    )
    interface_subsystem.save()
    soc_ip.add_child(interface_subsystem)
    
    # PCIe interface
    pcie_interface = IP(
        name="PCIe_Gen4_x16_Controller",
        type_id=pcie_type.id,
        process_id=tsmc_process.id,
        revision="5.0",
        status="production",
        provider="Synopsys",
        description="PCIe Gen4 x16 controller for high-speed expansion"
    )
    pcie_interface.save()
    interface_subsystem.add_child(pcie_interface)
    
    # USB interface
    usb_interface = IP(
        name="USB_3.2_Gen2_Controller",
        type_id=usb_type.id,
        process_id=tsmc_process.id,
        revision="3.2",
        status="production",
        provider="Synopsys",
        description="USB 3.2 Gen2 controller for high-speed data transfer"
    )
    usb_interface.save()
    interface_subsystem.add_child(usb_interface)
    
    # Ethernet interface
    ethernet_interface = IP(
        name="10G_Ethernet_MAC",
        type_id=ethernet_type.id,
        process_id=tsmc_process.id,
        revision="2.1",
        status="production",
        provider="TSMC",
        description="10 Gigabit Ethernet MAC controller"
    )
    ethernet_interface.save()
    interface_subsystem.add_child(ethernet_interface)
    
    # Peripheral Subsystem
    peripheral_subsystem = IP(
        name="Peripheral_Subsystem",
        type_id=peripheral_type.id,
        process_id=tsmc_process.id,
        revision="1.0",
        status="production",
        provider="TSMC",
        description="Peripheral subsystem with various system peripherals"
    )
    peripheral_subsystem.save()
    soc_ip.add_child(peripheral_subsystem)
    
    # UART controllers
    uart1 = IP(
        name="UART_Controller_1",
        type_id=uart_type.id,
        process_id=tsmc_process.id,
        revision="1.0",
        status="production",
        provider="TSMC",
        description="UART controller for serial communication"
    )
    uart1.save()
    peripheral_subsystem.add_child(uart1)
    
    uart2 = IP(
        name="UART_Controller_2",
        type_id=uart_type.id,
        process_id=tsmc_process.id,
        revision="1.0",
        status="production",
        provider="TSMC",
        description="UART controller for serial communication"
    )
    uart2.save()
    peripheral_subsystem.add_child(uart2)
    
    # GPIO controller
    gpio_controller = IP(
        name="GPIO_Controller_64bit",
        type_id=gpio_type.id,
        process_id=tsmc_process.id,
        revision="1.0",
        status="production",
        provider="TSMC",
        description="64-bit GPIO controller for general purpose I/O"
    )
    gpio_controller.save()
    peripheral_subsystem.add_child(gpio_controller)
    
    # Timer controllers
    timer1 = IP(
        name="System_Timer",
        type_id=timer_type.id,
        process_id=tsmc_process.id,
        revision="1.0",
        status="production",
        provider="TSMC",
        description="System timer for OS scheduling"
    )
    timer1.save()
    peripheral_subsystem.add_child(timer1)
    
    timer2 = IP(
        name="Watchdog_Timer",
        type_id=timer_type.id,
        process_id=tsmc_process.id,
        revision="1.0",
        status="production",
        provider="TSMC",
        description="Watchdog timer for system monitoring"
    )
    timer2.save()
    peripheral_subsystem.add_child(timer2)
    
    # Mixed-Signal Subsystem
    mixed_signal_subsystem = IP(
        name="Mixed_Signal_Subsystem",
        type_id=mixed_signal_type.id,
        process_id=tsmc_process.id,
        revision="1.0",
        status="production",
        provider="TSMC",
        description="Mixed-signal subsystem with analog interfaces"
    )
    mixed_signal_subsystem.save()
    soc_ip.add_child(mixed_signal_subsystem)
    
    # ADC
    adc_ip = IP(
        name="12bit_ADC_1MSPS",
        type_id=adc_type.id,
        process_id=tsmc_process.id,
        revision="2.0",
        status="production",
        provider="TSMC",
        description="12-bit ADC with 1MSPS sampling rate"
    )
    adc_ip.save()
    mixed_signal_subsystem.add_child(adc_ip)
    
    # DAC
    dac_ip = IP(
        name="10bit_DAC_500KSPS",
        type_id=dac_type.id,
        process_id=tsmc_process.id,
        revision="1.5",
        status="production",
        provider="TSMC",
        description="10-bit DAC with 500KSPS output rate"
    )
    dac_ip.save()
    mixed_signal_subsystem.add_child(dac_ip)
    
    print("Hierarchical IP structure created successfully!")
    
    # Display the hierarchy
    print("\n5. Displaying IP hierarchy...")
    ip_manager.show_ip_tree(ip_name="TSMC_7nm_SoC_v1.0")
    
    # Demonstrate finding IPs
    print("\n6. Finding IPs...")
    
    # Find all root IPs
    root_ips = IP.find_roots()
    print(f"Root IPs ({len(root_ips)}):")
    for ip in root_ips:
        print(f"  - {ip.name}")
    
    # Find by process
    tsmc_ips = ip_manager.find(process_name="TSMC_7nm_SoC_Design")
    print(f"TSMC Process IPs ({len(tsmc_ips)}):")
    for ip in tsmc_ips:
        type_obj = ip.get_type()
        print(f"  - {ip.name} (Type: {type_obj.name if type_obj else 'Unknown'})")
    
    # Find by type tree
    processor_ips = ip_manager.find_by_type_tree("Processor", include_descendants=True)
    print(f"Processor IPs ({len(processor_ips)}):")
    for ip in processor_ips:
        type_obj = ip.get_type()
        print(f"  - {ip.name} (Type: {type_obj.name if type_obj else 'Unknown'})")
    
    # Demonstrate hierarchical operations
    print("\n7. Hierarchical operations...")
    
    # Get complete hierarchy
    hierarchy = ip_manager.get_ip_hierarchy("TSMC_7nm_SoC_v1.0")
    print("Complete SoC hierarchy:")
    print_hierarchy_dict(hierarchy, 0)
    
    # Demonstrate different tree viewing options
    print("\n8. Tree viewing options...")
    
    # Show tree by process
    print("\nIPs by process:")
    ip_manager.show_ip_tree_by_process("TSMC_7nm_SoC_Design")
    
    # Show tree by type
    print("\nIPs by type (Processor):")
    ip_manager.show_ip_tree_by_type("Processor")
    
    # Show detailed tree
    print("\nDetailed IP tree:")
    ip_manager.show_ip_tree(ip_name="TSMC_7nm_SoC_v1.0", show_details=True)
    
    # Get all descendants of CPU subsystem
    cpu_subsystem = IP.find_by_name("CPU_Subsystem")
    descendants = cpu_subsystem.get_all_descendants()
    print(f"\nCPU Subsystem descendants ({len(descendants)}):")
    for ip in descendants:
        type_obj = ip.get_type()
        print(f"  - {ip.name} (Type: {type_obj.name if type_obj else 'Unknown'})")
    
    # Pack IPs for export
    print("\n9. Packing IPs for export...")
    packed_data = ip_manager.pack({"process_name": "TSMC_7nm_SoC_Design"})
    print(f"Packed {packed_data['metadata']['total_ips']} TSMC IPs")
    
    print("\nExample completed successfully!")

def print_type_tree(types=None, level=0):
    """Print type tree structure"""
    if types is None:
        types = Type.find_roots()
    
    for type_obj in types:
        indent = "  " * level
        print(f"{indent}├─ {type_obj.name}")
        children = type_obj.find_children()
        if children:
            print_type_tree(children, level + 1)

def print_ip_hierarchy(ip, level=0):
    """Print IP hierarchy structure"""
    indent = "  " * level
    type_obj = ip.get_type()
    print(f"{indent}├─ {ip.name} ({type_obj.name if type_obj else 'Unknown'}) - {ip.status}")
    
    children = ip.get_children()
    for child in children:
        print_ip_hierarchy(child, level + 1)

def print_hierarchy_dict(hierarchy, level=0):
    """Print hierarchy dictionary structure"""
    indent = "  " * level
    print(f"{indent}├─ {hierarchy['name']} ({hierarchy['type']}) - {hierarchy['status']}")
    
    for child in hierarchy['children']:
        print_hierarchy_dict(child, level + 1)

if __name__ == "__main__":
    main()