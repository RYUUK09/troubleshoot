"""Generator for evaluation test dataset and sample expert proposals."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

# Authentic Evaluation Test Dataset (26 test cases)
TEST_CASES = [
    # --- NETWORK CASES ---
    {
        "test_id": "TC-NET-01",
        "domain": "Network Troubleshooting",
        "name": "Wi-Fi Adapter Disabled Scenario",
        "facts": {
            "wifi_adapter_enabled": "NO"
        },
        "expected_diagnosis": "Wi-Fi Adapter Disabled or Hardware Faulty",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-NET-02",
        "domain": "Network Troubleshooting",
        "name": "Weak Signal Interference",
        "facts": {
            "wifi_adapter_enabled": "YES",
            "local_network_connected": "YES",
            "wi_fi_signal_strong": "NO"
        },
        "expected_diagnosis": "Wi-Fi Signal Degradation and Physical Interference",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-NET-03",
        "domain": "Network Troubleshooting",
        "name": "Public IP Pingable But DNS Unresponsive",
        "facts": {
            "wifi_adapter_enabled": "YES",
            "local_network_connected": "YES",
            "router_gateway_ping_success": "YES",
            "public_ip_ping_success": "YES",
            "dns_domain_resolves": "NO"
        },
        "expected_diagnosis": "DNS Server Resolution Failure",
        "category": "Multi-Level Backward Chaining"
    },
    {
        "test_id": "TC-NET-04",
        "domain": "Network Troubleshooting",
        "name": "Captive Portal Splash Screen Intercept",
        "facts": {
            "wifi_adapter_enabled": "YES",
            "local_network_connected": "YES",
            "router_gateway_ping_success": "YES",
            "public_ip_ping_success": "NO",
            "captive_portal_detected": "YES"
        },
        "expected_diagnosis": "Unauthenticated Captive Portal Interception",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-NET-05",
        "domain": "Network Troubleshooting",
        "name": "ISP Upstream Fiber Outage",
        "facts": {
            "wifi_adapter_enabled": "YES",
            "local_network_connected": "YES",
            "router_gateway_ping_success": "YES",
            "public_ip_ping_success": "NO",
            "router_internet_light_green": "NO",
            "captive_portal_detected": "NO"
        },
        "expected_diagnosis": "ISP Upstream Service Outage or Fiber Cut",
        "category": "Multi-Level Backward Chaining"
    },
    {
        "test_id": "TC-NET-06",
        "domain": "Network Troubleshooting",
        "name": "Local Subnet IP Collision",
        "facts": {
            "wifi_adapter_enabled": "YES",
            "local_network_connected": "YES",
            "duplicate_ip_alert": "YES"
        },
        "expected_diagnosis": "IP Address Conflict on Local Subnet",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-NET-07",
        "domain": "Network Troubleshooting",
        "name": "Fully Operational Link",
        "facts": {
            "wifi_adapter_enabled": "YES",
            "local_network_connected": "YES",
            "router_gateway_ping_success": "YES",
            "public_ip_ping_success": "YES",
            "dns_domain_resolves": "YES",
            "wi_fi_signal_strong": "YES"
        },
        "expected_diagnosis": "Fully Operational Network and DNS Resolution",
        "category": "Full Stack Verification"
    },
    # Novel network case: Ethernet Mesh Backhaul Spanning Tree Loop (handled by Expert Rule!)
    {
        "test_id": "TC-NET-08",
        "domain": "Network Troubleshooting",
        "name": "Mesh Wi-Fi STP Broadcast Storm Loop",
        "facts": {
            "wifi_adapter_enabled": "YES",
            "local_network_connected": "YES",
            "router_gateway_ping_success": "NO",
            "mesh_satellite_ethernet_backhaul": "YES",
            "switch_port_blinking_furious": "YES"
        },
        "expected_diagnosis": "Spanning Tree Protocol Loop / Ethernet Backhaul Broadcast Storm",
        "category": "Novel Scenario (Expert Learning Test)"
    },

    # --- SOFTWARE CASES ---
    {
        "test_id": "TC-SOFT-01",
        "domain": "Software Troubleshooting",
        "name": "OS Architecture Incompatibility",
        "facts": {
            "system_meets_minimum_os_version": "NO"
        },
        "expected_diagnosis": "Operating System Architecture or Version Incompatibility",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-SOFT-02",
        "domain": "Software Troubleshooting",
        "name": "Disk Exhaustion",
        "facts": {
            "available_disk_space_sufficient": "NO"
        },
        "expected_diagnosis": "Insufficient System Storage / Disk Full",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-SOFT-03",
        "domain": "Software Troubleshooting",
        "name": "Missing Visual C++ Runtime DLL",
        "facts": {
            "system_meets_minimum_os_version": "YES",
            "available_disk_space_sufficient": "YES",
            "visual_c_runtimes_installed": "NO",
            "error_code_missing_dll": "YES"
        },
        "expected_diagnosis": "Missing Dynamic Link Libraries (C++ / .NET Runtimes)",
        "category": "Multi-Level Backward Chaining"
    },
    {
        "test_id": "TC-SOFT-04",
        "domain": "Software Troubleshooting",
        "name": "Antivirus Quarantine Lockout",
        "facts": {
            "antivirus_quarantine_alert": "YES",
            "app_opens_at_all": "NO"
        },
        "expected_diagnosis": "Antivirus Quarantine Lock or False-Positive Block",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-SOFT-05",
        "domain": "Software Troubleshooting",
        "name": "UAC Privileges Rejected",
        "facts": {
            "system_meets_minimum_os_version": "YES",
            "available_disk_space_sufficient": "YES",
            "app_launched_as_administrator": "NO",
            "config_cache_folder_writable": "NO"
        },
        "expected_diagnosis": "Insufficient User Access Permissions (UAC / File System ACLs)",
        "category": "Multi-Level Backward Chaining"
    },
    {
        "test_id": "TC-SOFT-06",
        "domain": "Software Troubleshooting",
        "name": "Memory Leak Freeze",
        "facts": {
            "app_opens_at_all": "YES",
            "high_memory_usage_freeze": "YES"
        },
        "expected_diagnosis": "Application Memory Leak / Out-of-Memory Freeze",
        "category": "Clear Confirmation"
    },
    # Novel software case: Port 8080/5000 Socket Bind Collision (handled by Expert Rule!)
    {
        "test_id": "TC-SOFT-07",
        "domain": "Software Troubleshooting",
        "name": "Local Server Port Binding Collision",
        "facts": {
            "system_meets_minimum_os_version": "YES",
            "available_disk_space_sufficient": "YES",
            "error_code_missing_dll": "NO",
            "socket_address_already_in_use_error": "YES"
        },
        "expected_diagnosis": "TCP Socket Address Already in Use (Port Collision)",
        "category": "Novel Scenario (Expert Learning Test)"
    },

    # --- VEHICLE CASES ---
    {
        "test_id": "TC-VEH-01",
        "domain": "Vehicle Troubleshooting",
        "name": "Completely Dead Battery",
        "facts": {
            "dashboard_lights_illuminate": "NO"
        },
        "expected_diagnosis": "Depleted or Discharged 12V Starter Battery",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-VEH-02",
        "domain": "Vehicle Troubleshooting",
        "name": "Starter Solenoid Clicking Chatter",
        "facts": {
            "dashboard_lights_illuminate": "YES",
            "starter_rapid_clicking_sound": "YES"
        },
        "expected_diagnosis": "Low Battery Voltage Causing Starter Solenoid Chatter",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-VEH-03",
        "domain": "Vehicle Troubleshooting",
        "name": "Starter Motor Circuit Fault",
        "facts": {
            "dashboard_lights_illuminate": "YES",
            "starter_rapid_clicking_sound": "NO",
            "starter_motor_cranks_engine": "NO"
        },
        "expected_diagnosis": "Faulty Starter Motor or Starter Relay Circuit",
        "category": "Multi-Level Backward Chaining"
    },
    {
        "test_id": "TC-VEH-04",
        "domain": "Vehicle Troubleshooting",
        "name": "Engine Cranks But Empty Fuel Tank",
        "facts": {
            "dashboard_lights_illuminate": "YES",
            "starter_rapid_clicking_sound": "NO",
            "starter_motor_cranks_engine": "YES",
            "fuel_level_sufficient": "NO"
        },
        "expected_diagnosis": "Fuel Starvation or Depleted Fuel Tank",
        "category": "Multi-Level Backward Chaining"
    },
    {
        "test_id": "TC-VEH-05",
        "domain": "Vehicle Troubleshooting",
        "name": "Boiling Radiator Coolant Emergency",
        "facts": {
            "engine_overheating_gauge_in_red": "YES",
            "steam_escaping_from_hood": "YES"
        },
        "expected_diagnosis": "CRITICAL: Severe Engine Thermal Overheating / Coolant Loss",
        "category": "Safety Critical Scenario"
    },
    {
        "test_id": "TC-VEH-06",
        "domain": "Vehicle Troubleshooting",
        "name": "Tyre Puncture with Audible Hiss",
        "facts": {
            "tyre_pressure_warning_light_on": "YES",
            "audible_tyre_air_hiss": "YES"
        },
        "expected_diagnosis": "Tyre Pressure Deflation / Slow Tread Puncture",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-VEH-07",
        "domain": "Vehicle Troubleshooting",
        "name": "Acoustic Brake Wear Squeal",
        "facts": {
            "brake_wear_indicator_squeal": "YES"
        },
        "expected_diagnosis": "Brake Friction Pad Material Wear / Acoustic Sensor Alert",
        "category": "Clear Confirmation"
    },

    # --- IOT & HARDWARE CASES ---
    {
        "test_id": "TC-IOT-01",
        "domain": "IoT & Hardware Troubleshooting",
        "name": "Unpowered MCU Board",
        "facts": {
            "mcu_power_led_lit": "NO"
        },
        "expected_diagnosis": "Total Board Power Deprivation / Open Circuit",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-IOT-02",
        "domain": "IoT & Hardware Troubleshooting",
        "name": "ESP32 RF Transmit Brownout",
        "facts": {
            "mcu_power_led_lit": "YES",
            "supply_voltage_drops_under_load": "YES"
        },
        "expected_diagnosis": "Power Supply Brownout Under Radio Frequency Transmit Peak",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-IOT-03",
        "domain": "IoT & Hardware Troubleshooting",
        "name": "Missing USB UART Driver",
        "facts": {
            "mcu_power_led_lit": "YES",
            "usb_port_recognized_in_os": "NO"
        },
        "expected_diagnosis": "Missing USB-to-UART Bridge Driver (CH340 / CP2102)",
        "category": "Clear Confirmation"
    },
    {
        "test_id": "TC-IOT-04",
        "domain": "IoT & Hardware Troubleshooting",
        "name": "ESP Flash Mode GPIO0 Bootloader Timeout",
        "facts": {
            "mcu_power_led_lit": "YES",
            "supply_voltage_drops_under_load": "NO",
            "usb_port_recognized_in_os": "YES",
            "firmware_upload_timed_out": "YES",
            "boot_button_pressed_during_flash": "NO"
        },
        "expected_diagnosis": "Microcontroller Bootloader Synchronization Failure",
        "category": "Multi-Level Backward Chaining"
    },
    {
        "test_id": "TC-IOT-05",
        "domain": "IoT & Hardware Troubleshooting",
        "name": "I2C Floating Lines Without Pullups",
        "facts": {
            "mcu_power_led_lit": "YES",
            "supply_voltage_drops_under_load": "NO",
            "pull_up_resistors_installed": "NO",
            "i2c_bus_scanner_detects_address": "NO"
        },
        "expected_diagnosis": "Floating I2C Bus / Missing Bus Pull-Up Resistors",
        "category": "Multi-Level Backward Chaining"
    },
    {
        "test_id": "TC-IOT-06",
        "domain": "IoT & Hardware Troubleshooting",
        "name": "5V to 3.3V Logic Level Incompatibility",
        "facts": {
            "mcu_power_led_lit": "YES",
            "supply_voltage_drops_under_load": "NO",
            "logic_voltage_level_matched": "NO"
        },
        "expected_diagnosis": "Logic Voltage Level Clamping / Incompatible Thresholds",
        "category": "Multi-Level Backward Chaining"
    }
]

# Write evaluation dataset
with open(DATA_DIR / "evaluation_testset.json", "w", encoding="utf-8") as f:
    json.dump({"total_cases": len(TEST_CASES), "test_cases": TEST_CASES}, f, indent=2)

# Sample Expert Proposals (Demonstrating the Expert Review Workflow)
EXPERT_PROPOSALS = [
    {
        "proposal_id": "EXP-PROP-001",
        "rule_id": "R-NET-EXP-001",
        "domain": "Network Troubleshooting",
        "diagnosis": "Spanning Tree Protocol Loop / Ethernet Backhaul Broadcast Storm",
        "conditions": [
            {"fact": "local_network_connected", "expected_value": "YES", "description": "Is your device connected to the local Wi-Fi network / Access Point?", "is_intermediate": False},
            {"fact": "router_gateway_ping_success", "expected_value": "NO", "description": "Can your device successfully ping the local default gateway IP (e.g. 192.168.1.1)?", "is_intermediate": False},
            {"fact": "mesh_satellite_ethernet_backhaul", "expected_value": "YES", "description": "Are mesh access point satellites connected via wired Ethernet backhaul switches?", "is_intermediate": False},
            {"fact": "switch_port_blinking_furious", "expected_value": "YES", "description": "Are network switch port activity lights flashing continuously at extreme frequency (broadcast storm)?", "is_intermediate": False}
        ],
        "explanation": "An unmanaged switch without IEEE 802.1D/w STP has formed a bridging loop between wired and wireless backhauls, causing packet storm saturation.",
        "solution": "1. Temporarily unplug the Ethernet cable from the satellite mesh nodes.\n2. Enable Spanning Tree Protocol (STP/RSTP) in your managed switch configuration.\n3. Verify whether your mesh system supports simultaneous wired backhaul or requires AP isolation.",
        "approval_status": "APPROVED",
        "author": "Dr. Sarah Lin (Senior Network Architect)",
        "created_at": "2026-10-31",
        "reviewed_by": "Chief Expert Reviewer",
        "review_notes": "Validated: Solves frequent mesh network bridging storms reported in enterprise and home installations."
    },
    {
        "proposal_id": "EXP-PROP-002",
        "rule_id": "R-SOFT-EXP-001",
        "domain": "Software Troubleshooting",
        "diagnosis": "TCP Socket Address Already in Use (Port Collision)",
        "conditions": [
            {"fact": "system_meets_minimum_os_version", "expected_value": "YES", "description": "Does your computer meet the software's minimum OS version and architecture requirements?", "is_intermediate": False},
            {"fact": "available_disk_space_sufficient", "expected_value": "YES", "description": "Do you have at least 5 GB of free storage space on your system partition?", "is_intermediate": False},
            {"fact": "error_code_missing_dll", "expected_value": "NO", "description": "Does an error dialog specifically mention missing DLLs?", "is_intermediate": False},
            {"fact": "socket_address_already_in_use_error", "expected_value": "YES", "description": "Does application console output report 'Errno 98 / 10048: Address already in use' or port bind collision?", "is_intermediate": False}
        ],
        "explanation": "Another active process or orphaned daemon has already bound exclusively to the designated TCP/IP listening socket.",
        "solution": "1. Run 'netstat -ano | findstr <port_number>' in terminal to identify the conflicting PID.\n2. Terminate the blocking process via 'taskkill /PID <pid> /F' or Task Manager.\n3. Alternatively, reconfigure the application port setting to an available port.",
        "approval_status": "APPROVED",
        "author": "DevOps Engineer Alex Kumar",
        "created_at": "2026-10-31",
        "reviewed_by": "Lead Software Systems Reviewer",
        "review_notes": "Crucial addition for developer and server software runtime troubleshooting."
    },
    {
        "proposal_id": "EXP-PROP-003",
        "rule_id": "R-IOT-EXP-001",
        "domain": "IoT & Hardware Troubleshooting",
        "diagnosis": "SPI Bus Clock Phase/Polarity (CPOL/CPHA Mode) Inversion",
        "conditions": [
            {"fact": "mcu_power_led_lit", "expected_value": "YES", "description": "Is the onboard Power LED steadily illuminated?", "is_intermediate": False},
            {"fact": "spi_data_shifted_by_one_bit", "expected_value": "YES", "description": "Are SPI sensor register bytes arriving bit-shifted or inverted (e.g. 0xAA received as 0x55)?", "is_intermediate": False}
        ],
        "explanation": "The microcontroller SPI master is sampling data on the wrong clock edge (Mode 0 vs Mode 3 mismatch).",
        "solution": "1. Check the sensor datasheet for SPI Mode specification (CPOL 0/1, CPHA 0/1).\n2. Update SPI.beginTransaction(SPISettings(..., SPI_MODE0/1/2/3)) in firmware.",
        "approval_status": "PENDING_REVIEW",
        "author": "Embedded Systems Engineer Maria R.",
        "created_at": "2026-10-31",
        "reviewed_by": None,
        "review_notes": "Under review for formal bus timing verification."
    }
]

with open(DATA_DIR / "expert_proposals.json", "w", encoding="utf-8") as f:
    json.dump(EXPERT_PROPOSALS, f, indent=2)

# Initialize empty history logs if not existing
if not (DATA_DIR / "diagnosis_history.json").exists():
    with open(DATA_DIR / "diagnosis_history.json", "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)

if not (DATA_DIR / "evaluation_history.json").exists():
    with open(DATA_DIR / "evaluation_history.json", "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)

print(f"Generated {len(TEST_CASES)} evaluation test cases and {len(EXPERT_PROPOSALS)} expert proposals.")
