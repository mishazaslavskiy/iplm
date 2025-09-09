#!/usr/bin/env python3
"""
Basic usage examples for IPLM
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import Process, IP, Type, ip_manager, db_manager

def main():
    """Basic usage examples"""
    print("IPLM Basic Usage Examples")
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
    digital_type.save()
    analog_type.save()
    
    # Child types
    cpu_type = Type(name="CPU", parent_id=digital_type.id, description="CPU cores")
    memory_type = Type(name="Memory", parent_id=digital_type.id, description="Memory controllers")
    adc_type = Type(name="ADC", parent_id=analog_type.id, description="Analog-to-Digital converters")
    
    cpu_type.save()
    memory_type.save()
    adc_type.save()
    
    # Grandchild types
    arm_type = Type(name="ARM", parent_id=cpu_type.id, description="ARM processor cores")
    riscv_type = Type(name="RISC-V", parent_id=cpu_type.id, description="RISC-V processor cores")
    
    arm_type.save()
    riscv_type.save()
    
    print("Type hierarchy created:")
    print_type_tree()
    
    # Create processes
    print("\n3. Creating processes...")
    
    process1 = Process(
        name="SoC_Design_v1",
        node="28nm",
        fab="TSMC",
        description="Main SoC design process"
    )
    process1.save()
    
    process2 = Process(
        name="AI_Accelerator_v2",
        node="7nm",
        fab="Samsung",
        description="AI accelerator design process"
    )
    process2.save()
    
    print("Processes created:")
    for process in Process.find_all():
        print(f"  - {process.name} (Node: {process.node}, FAB: {process.fab})")
    
    # Create IPs
    print("\n4. Creating IPs...")
    
    # ARM Cortex-A78 IP
    arm_ip = IP(
        name="ARM_Cortex_A78_1GHz",
        type_id=arm_type.id,
        process_id=process1.id,
        revision="2.1",
        status="production",
        provider="ARM Ltd.",
        flavor="high-performance",
        description="High-performance ARM Cortex-A78 core at 1GHz",
        documentation="https://developer.arm.com/ip-products/processors/cortex-a/cortex-a78"
    )
    arm_ip.add_component({"name": "L1_I_Cache", "size": "32KB", "associativity": 4})
    arm_ip.add_component({"name": "L1_D_Cache", "size": "32KB", "associativity": 4})
    arm_ip.add_component({"name": "L2_Cache", "size": "256KB", "associativity": 8})
    arm_ip.save()
    
    # RISC-V IP
    riscv_ip = IP(
        name="RISC_V_RV64GC_800MHz",
        type_id=riscv_type.id,
        process_id=process2.id,
        revision="1.0",
        status="beta",
        provider="SiFive",
        flavor="low-power",
        description="RISC-V RV64GC core at 800MHz",
        documentation="https://www.sifive.com/cores/risc-v-core-ip"
    )
    riscv_ip.add_component({"name": "L1_I_Cache", "size": "16KB", "associativity": 2})
    riscv_ip.add_component({"name": "L1_D_Cache", "size": "16KB", "associativity": 2})
    riscv_ip.save()
    
    # Memory controller IP
    memory_ip = IP(
        name="DDR4_Controller_3200MHz",
        type_id=memory_type.id,
        process_id=process1.id,
        revision="3.2",
        status="production",
        provider="Synopsys",
        flavor="high-speed",
        description="DDR4 memory controller supporting up to 3200MHz",
        documentation="https://www.synopsys.com/dw/ipdir.php?ds=dwc_ddr4_controller"
    )
    memory_ip.add_component({"name": "PHY", "type": "DDR4", "speed": "3200MHz"})
    memory_ip.add_component({"name": "Controller", "channels": 2, "data_width": 64})
    memory_ip.save()
    
    print("IPs created:")
    for ip in IP.find_all():
        type_obj = ip.get_type()
        process = ip.get_process()
        print(f"  - {ip.name} (Type: {type_obj.name if type_obj else 'Unknown'}, "
              f"Process: {process.name if process else 'Unknown'}, Status: {ip.status})")
    
    # Demonstrate finding IPs
    print("\n5. Finding IPs...")
    
    # Find by status
    production_ips = ip_manager.find(status="production")
    print(f"Production IPs ({len(production_ips)}):")
    for ip in production_ips:
        print(f"  - {ip.name}")
    
    # Find by type tree
    digital_ips = ip_manager.find_by_type_tree("Digital", include_descendants=True)
    print(f"Digital IPs ({len(digital_ips)}):")
    for ip in digital_ips:
        type_obj = ip.get_type()
        print(f"  - {ip.name} (Type: {type_obj.name if type_obj else 'Unknown'})")
    
    # Find by process
    soc_ips = ip_manager.find(process_name="SoC_Design_v1")
    print(f"SoC Design IPs ({len(soc_ips)}):")
    for ip in soc_ips:
        print(f"  - {ip.name}")
    
    # Demonstrate IP operations
    print("\n6. IP operations...")
    
    # Update IP status
    print("Updating RISC-V IP status to production...")
    if ip_manager.update("RISC_V_RV64GC_800MHz", status="production"):
        print("Status updated successfully!")
    
    # Release IP (change to production)
    print("Releasing ARM IP...")
    if ip_manager.release("ARM_Cortex_A78_1GHz"):
        print("ARM IP released successfully!")
    
    # Pack IPs for export
    print("\n7. Packing IPs for export...")
    packed_data = ip_manager.pack({"status": "production"})
    print(f"Packed {packed_data['metadata']['total_ips']} production IPs")
    
    # Show final IP status
    print("\n8. Final IP status:")
    for ip in IP.find_all():
        type_obj = ip.get_type()
        process = ip.get_process()
        print(f"  - {ip.name}: {ip.status} (Type: {type_obj.name if type_obj else 'Unknown'}, "
              f"Process: {process.name if process else 'Unknown'})")
    
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

if __name__ == "__main__":
    main()
