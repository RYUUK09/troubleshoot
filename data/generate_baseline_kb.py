"""Generator script to build and validate baseline knowledge base and evaluation test dataset."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

# Define rules for all 4 domains
BASELINE_RULES = [
    # =========================================================================
    # DOMAIN 1: NETWORK TROUBLESHOOTING
    # =========================================================================
    # Intermediate Rule: Local Link
    {
        "rule_id": "R-NET-INT-001",
        "domain": "Network Troubleshooting",
        "intermediate_fact": "local_link_established",
        "diagnosis": None,
        "conditions": [
            {"fact": "wifi_adapter_enabled", "expected_value": "YES", "description": "Is your device's Wi-Fi / network adapter enabled?", "is_intermediate": False},
            {"fact": "local_network_connected", "expected_value": "YES", "description": "Is your device connected to the local Wi-Fi network / Access Point?", "is_intermediate": False}
        ],
        "explanation": "Local physical or wireless link to the router is successfully established.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Intermediate Rule: LAN Functional
    {
        "rule_id": "R-NET-INT-002",
        "domain": "Network Troubleshooting",
        "intermediate_fact": "lan_communication_functional",
        "diagnosis": None,
        "conditions": [
            {"fact": "local_link_established", "expected_value": "YES", "description": "Local link established", "is_intermediate": True},
            {"fact": "router_gateway_ping_success", "expected_value": "YES", "description": "Can your device successfully ping the local default gateway IP (e.g. 192.168.1.1)?", "is_intermediate": False}
        ],
        "explanation": "Local Area Network bidirectional communication with the router gateway is working.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Intermediate Rule: WAN Present
    {
        "rule_id": "R-NET-INT-003",
        "domain": "Network Troubleshooting",
        "intermediate_fact": "wan_connectivity_present",
        "diagnosis": None,
        "conditions": [
            {"fact": "lan_communication_functional", "expected_value": "YES", "description": "LAN communication functional", "is_intermediate": True},
            {"fact": "public_ip_ping_success", "expected_value": "YES", "description": "Can your device successfully ping a public IP address (such as 8.8.8.8 or 1.1.1.1)?", "is_intermediate": False}
        ],
        "explanation": "Packets can traverse through the gateway router onto the global internet.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 1: Wi-Fi Adapter Disabled
    {
        "rule_id": "R-NET-001",
        "domain": "Network Troubleshooting",
        "diagnosis": "Wi-Fi Adapter Disabled or Hardware Faulty",
        "conditions": [
            {"fact": "wifi_adapter_enabled", "expected_value": "NO", "description": "Is your device's Wi-Fi / network adapter enabled?", "is_intermediate": False}
        ],
        "explanation": "The operating system reports that the wireless network interface card is disabled, in airplane mode, or missing hardware drivers.",
        "solution": "1. Open Network Settings or Device Manager.\n2. Ensure Airplane Mode is toggled OFF.\n3. Right-click your Wi-Fi interface and select 'Enable Device'.\n4. If missing, reinstall the wireless adapter driver from the manufacturer's website.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 2: Wi-Fi Signal Degradation
    {
        "rule_id": "R-NET-002",
        "domain": "Network Troubleshooting",
        "diagnosis": "Wi-Fi Signal Degradation and Physical Interference",
        "conditions": [
            {"fact": "wifi_adapter_enabled", "expected_value": "YES", "description": "Is your device's Wi-Fi / network adapter enabled?", "is_intermediate": False},
            {"fact": "local_network_connected", "expected_value": "YES", "description": "Is your device connected to the local Wi-Fi network / Access Point?", "is_intermediate": False},
            {"fact": "wi_fi_signal_strong", "expected_value": "NO", "description": "Is the Wi-Fi signal indicator strong (3 or more bars)?", "is_intermediate": False}
        ],
        "explanation": "The wireless link is active but suffering from severe RSSI signal attenuation or 2.4 GHz channel interference from obstacles or appliances.",
        "solution": "1. Move closer to the wireless access point.\n2. Switch to the 5 GHz Wi-Fi frequency band if available.\n3. Keep the router away from thick reinforced walls, metal enclosures, and microwaves.\n4. Change the Wi-Fi broadcast channel on the router (e.g. Channel 1, 6, or 11).",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 3: Gateway DHCP Failure
    {
        "rule_id": "R-NET-003",
        "domain": "Network Troubleshooting",
        "diagnosis": "Default Gateway or DHCP Assignment Failure",
        "conditions": [
            {"fact": "local_link_established", "expected_value": "YES", "description": "Local link established", "is_intermediate": True},
            {"fact": "router_gateway_ping_success", "expected_value": "NO", "description": "Can your device successfully ping the local default gateway IP (e.g. 192.168.1.1)?", "is_intermediate": False},
            {"fact": "other_devices_connect", "expected_value": "YES", "description": "Can other smartphones or computers connect and browse on this same network?", "is_intermediate": False}
        ],
        "explanation": "The client device has associated with the SSID but did not receive a valid IP/Gateway address lease from the DHCP pool.",
        "solution": "1. Open terminal and run 'ipconfig /release' followed by 'ipconfig /renew'.\n2. Verify TCP/IPv4 properties are set to 'Obtain an IP address automatically'.\n3. Forget the Wi-Fi network and reconnect with the security passphrase.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 4: IP Address Conflict
    {
        "rule_id": "R-NET-004",
        "domain": "Network Troubleshooting",
        "diagnosis": "IP Address Conflict on Local Subnet",
        "conditions": [
            {"fact": "local_link_established", "expected_value": "YES", "description": "Local link established", "is_intermediate": True},
            {"fact": "duplicate_ip_alert", "expected_value": "YES", "description": "Did the operating system report an IP address conflict with another device on the network?", "is_intermediate": False}
        ],
        "explanation": "Two distinct network nodes have been assigned the same static or DHCP IP address, creating ARP collisions and dropping packets.",
        "solution": "1. Set client adapter configuration back to dynamic DHCP assignment.\n2. Check router DHCP scope to ensure static IP reservations do not overlap with the dynamic pool.\n3. Restart the router to clear stale ARP cache tables.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 5: Captive Portal Authentication
    {
        "rule_id": "R-NET-005",
        "domain": "Network Troubleshooting",
        "diagnosis": "Unauthenticated Captive Portal Interception",
        "conditions": [
            {"fact": "lan_communication_functional", "expected_value": "YES", "description": "LAN communication functional", "is_intermediate": True},
            {"fact": "public_ip_ping_success", "expected_value": "NO", "description": "Can your device successfully ping a public IP address (such as 8.8.8.8 or 1.1.1.1)?", "is_intermediate": False},
            {"fact": "captive_portal_detected", "expected_value": "YES", "description": "Does opening a browser attempt to redirect you to a Wi-Fi splash or terms acceptance page?", "is_intermediate": False}
        ],
        "explanation": "The gateway firewall is actively intercepting and blocking external IP transit pending web-based splash page authentication.",
        "solution": "1. Open a browser and navigate to 'http://neverssl.com' or 'http://1.1.1.1' to trigger the portal.\n2. Accept terms of service or enter the required guest access credentials.\n3. Disable third-party secure DNS temporarily if it prevents portal interception.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 6: DNS Server Resolution Failure
    {
        "rule_id": "R-NET-006",
        "domain": "Network Troubleshooting",
        "diagnosis": "DNS Server Resolution Failure",
        "conditions": [
            {"fact": "wan_connectivity_present", "expected_value": "YES", "description": "WAN connectivity present", "is_intermediate": True},
            {"fact": "dns_domain_resolves", "expected_value": "NO", "description": "Can your device open websites by name (e.g. google.com or wikipedia.org)?", "is_intermediate": False}
        ],
        "explanation": "Direct TCP/IP routing to public internet hosts works, but domain name lookup via configured DNS resolvers is timing out.",
        "solution": "1. Flush local DNS resolver cache: run 'ipconfig /flushdns' in terminal.\n2. Configure reliable public DNS servers: Primary 1.1.1.1 (Cloudflare) and Secondary 8.8.8.8 (Google).\n3. Check if your router or ISP DNS is experiencing a temporary nameserver outage.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 7: ISP Upstream Outage
    {
        "rule_id": "R-NET-007",
        "domain": "Network Troubleshooting",
        "diagnosis": "ISP Upstream Service Outage or Fiber Cut",
        "conditions": [
            {"fact": "lan_communication_functional", "expected_value": "YES", "description": "LAN communication functional", "is_intermediate": True},
            {"fact": "public_ip_ping_success", "expected_value": "NO", "description": "Can your device successfully ping a public IP address (such as 8.8.8.8 or 1.1.1.1)?", "is_intermediate": False},
            {"fact": "router_internet_light_green", "expected_value": "NO", "description": "Is the WAN/Internet indicator LED on your router solid green?", "is_intermediate": False},
            {"fact": "captive_portal_detected", "expected_value": "NO", "description": "Does opening a browser attempt to redirect you to a Wi-Fi splash or terms acceptance page?", "is_intermediate": False}
        ],
        "explanation": "The local router is operating normally, but the WAN uplink port has lost link synchronization or ISP authentication.",
        "solution": "1. Power cycle the modem/router by disconnecting power for 30 seconds.\n2. Check physical fiber or DSL/cable patch cords for kinks or disconnections.\n3. Contact your Internet Service Provider to check for regional service disruptions.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 8: Misconfigured VPN / Proxy
    {
        "rule_id": "R-NET-008",
        "domain": "Network Troubleshooting",
        "diagnosis": "Misconfigured VPN Client or Proxy Routing Loop",
        "conditions": [
            {"fact": "lan_communication_functional", "expected_value": "YES", "description": "LAN communication functional", "is_intermediate": True},
            {"fact": "vpn_proxy_enabled", "expected_value": "YES", "description": "Is a VPN software client or custom corporate proxy active on your device?", "is_intermediate": False},
            {"fact": "other_devices_connect", "expected_value": "YES", "description": "Can other smartphones or computers connect and browse on this same network?", "is_intermediate": False},
            {"fact": "dns_domain_resolves", "expected_value": "NO", "description": "Can your device open websites by name (e.g. google.com or wikipedia.org)?", "is_intermediate": False}
        ],
        "explanation": "A local virtual network adapter or kill-switch is redirecting traffic through a disconnected or dead tunnel endpoint.",
        "solution": "1. Disconnect or temporarily close the VPN client.\n2. Open OS Internet Options -> Connections -> LAN Settings, and uncheck 'Use a proxy server'.\n3. Reset network stack: 'netsh winsock reset' and reboot.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 9: Operational Link
    {
        "rule_id": "R-NET-009",
        "domain": "Network Troubleshooting",
        "diagnosis": "Fully Operational Network and DNS Resolution",
        "conditions": [
            {"fact": "wan_connectivity_present", "expected_value": "YES", "description": "WAN connectivity present", "is_intermediate": True},
            {"fact": "dns_domain_resolves", "expected_value": "YES", "description": "Can your device open websites by name (e.g. google.com or wikipedia.org)?", "is_intermediate": False},
            {"fact": "wi_fi_signal_strong", "expected_value": "YES", "description": "Is the Wi-Fi signal indicator strong (3 or more bars)?", "is_intermediate": False}
        ],
        "explanation": "All layers of the local and wide area network protocol stack are verified healthy and communicating.",
        "solution": "No remediation required. The network connection is stable, fully authenticated, and resolving addresses correctly.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },

    # =========================================================================
    # DOMAIN 2: SOFTWARE TROUBLESHOOTING
    # =========================================================================
    # Intermediate Rule: Host Environment Compliant
    {
        "rule_id": "R-SOFT-INT-001",
        "domain": "Software Troubleshooting",
        "intermediate_fact": "host_environment_compliant",
        "diagnosis": None,
        "conditions": [
            {"fact": "system_meets_minimum_os_version", "expected_value": "YES", "description": "Does your computer meet the software's minimum OS version and architecture requirements?", "is_intermediate": False},
            {"fact": "available_disk_space_sufficient", "expected_value": "YES", "description": "Do you have at least 5 GB of free storage space on your system partition?", "is_intermediate": False}
        ],
        "explanation": "Hardware architecture and storage capacity meet baseline application specifications.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Intermediate Rule: Execution Permissions Granted
    {
        "rule_id": "R-SOFT-INT-002",
        "domain": "Software Troubleshooting",
        "intermediate_fact": "execution_permissions_granted",
        "diagnosis": None,
        "conditions": [
            {"fact": "app_launched_as_administrator", "expected_value": "YES", "description": "Was the program or installer executed with administrative or elevated privileges?", "is_intermediate": False},
            {"fact": "config_cache_folder_writable", "expected_value": "YES", "description": "Can files be created and modified inside the %LOCALAPPDATA% directory without access errors?", "is_intermediate": False}
        ],
        "explanation": "The security token possesses adequate discretionary access permissions to write configuration and runtime files.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 1: OS Incompatibility
    {
        "rule_id": "R-SOFT-001",
        "domain": "Software Troubleshooting",
        "diagnosis": "Operating System Architecture or Version Incompatibility",
        "conditions": [
            {"fact": "system_meets_minimum_os_version", "expected_value": "NO", "description": "Does your computer meet the software's minimum OS version and architecture requirements?", "is_intermediate": False}
        ],
        "explanation": "The application binary relies on system API entry points or 64-bit CPU features absent in your current OS build.",
        "solution": "1. Upgrade the operating system build to the supported release.\n2. If using 32-bit Windows, verify if a 32-bit legacy executable is provided.\n3. Right-click executable -> Properties -> Compatibility tab -> Run this program in compatibility mode.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 2: Insufficient Storage
    {
        "rule_id": "R-SOFT-002",
        "domain": "Software Troubleshooting",
        "diagnosis": "Insufficient System Storage / Disk Full",
        "conditions": [
            {"fact": "available_disk_space_sufficient", "expected_value": "NO", "description": "Do you have at least 5 GB of free storage space on your system partition?", "is_intermediate": False}
        ],
        "explanation": "The installation or runtime memory pagefile cannot allocate scratch files due to partition exhaustion.",
        "solution": "1. Run Disk Cleanup or Storage Sense on drive C:\n2. Empty the Recycle Bin and purge temporary files in '%TEMP%'.\n3. Move bulky media files or unused heavy games to an external drive.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 3: Missing Runtime DLLs
    {
        "rule_id": "R-SOFT-003",
        "domain": "Software Troubleshooting",
        "diagnosis": "Missing Dynamic Link Libraries (C++ / .NET Runtimes)",
        "conditions": [
            {"fact": "host_environment_compliant", "expected_value": "YES", "description": "Host environment compliant", "is_intermediate": True},
            {"fact": "visual_c_runtimes_installed", "expected_value": "NO", "description": "Are the required Microsoft Visual C++ Redistributable packages (2015-2022) installed?", "is_intermediate": False},
            {"fact": "error_code_missing_dll", "expected_value": "YES", "description": "Does an error dialog specifically mention missing DLLs (e.g. VCRUNTIME140.dll, MSVCP140.dll)?", "is_intermediate": False}
        ],
        "explanation": "The executable loader cannot resolve imported symbols because shared dynamic runtime redistributable binaries are uninstalled.",
        "solution": "1. Download and install the latest official Microsoft Visual C++ Redistributable (x64 and x86).\n2. Install or repair the .NET Framework / Desktop Runtime.\n3. Reboot the machine and relaunch the application.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 4: Antivirus Quarantine Lock
    {
        "rule_id": "R-SOFT-004",
        "domain": "Software Troubleshooting",
        "diagnosis": "Antivirus Quarantine Lock or False-Positive Block",
        "conditions": [
            {"fact": "antivirus_quarantine_alert", "expected_value": "YES", "description": "Did Windows Defender or third-party antivirus display a threat alert or quarantine notification?", "is_intermediate": False},
            {"fact": "app_opens_at_all", "expected_value": "NO", "description": "Does the application window launch or appear at all?", "is_intermediate": False}
        ],
        "explanation": "Heuristic endpoint protection has intercepted the process startup and isolated the executable file in an encrypted quarantine container.",
        "solution": "1. Verify that the software is from an authentic, trusted developer source.\n2. Open Windows Security -> Protection history.\n3. Restore the isolated item and add an exclusion rule for the verified installation directory.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 5: Corrupted Installer Package
    {
        "rule_id": "R-SOFT-005",
        "domain": "Software Troubleshooting",
        "diagnosis": "Corrupted Installation Package or Checksum Mismatch",
        "conditions": [
            {"fact": "host_environment_compliant", "expected_value": "YES", "description": "Host environment compliant", "is_intermediate": True},
            {"fact": "installer_corrupted_signature", "expected_value": "YES", "description": "Did the installer abort with a CRC, cabinet file error, or invalid digital signature prompt?", "is_intermediate": False}
        ],
        "explanation": "Data packets during download suffered transmission truncation or storage media sector corruption.",
        "solution": "1. Delete the downloaded setup file from your disk.\n2. Clear browser cache and redownload the installer over a stable connection.\n3. Compute SHA256 hash using 'Get-FileHash' to verify integrity against developer checksums.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 6: Permission Denied Access Violation
    {
        "rule_id": "R-SOFT-006",
        "domain": "Software Troubleshooting",
        "diagnosis": "Insufficient User Access Permissions (UAC / File System ACLs)",
        "conditions": [
            {"fact": "host_environment_compliant", "expected_value": "YES", "description": "Host environment compliant", "is_intermediate": True},
            {"fact": "app_launched_as_administrator", "expected_value": "NO", "description": "Was the program or installer executed with administrative or elevated privileges?", "is_intermediate": False},
            {"fact": "config_cache_folder_writable", "expected_value": "NO", "description": "Can files be created and modified inside the %LOCALAPPDATA% directory without access errors?", "is_intermediate": False}
        ],
        "explanation": "Standard non-privileged user security context was rejected by Windows UAC when attempting to write system registry or program folders.",
        "solution": "1. Right-click the application executable or shortcut and choose 'Run as Administrator'.\n2. Inspect folder security permissions: ensure your Windows account has 'Full Control' over the app folder.\n3. Avoid installing standalone tools directly into protected root directories.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 7: Memory Exhaustion / OOM Freeze
    {
        "rule_id": "R-SOFT-007",
        "domain": "Software Troubleshooting",
        "diagnosis": "Application Memory Leak / Out-of-Memory Freeze",
        "conditions": [
            {"fact": "app_opens_at_all", "expected_value": "YES", "description": "Does the application window launch or appear at all?", "is_intermediate": False},
            {"fact": "high_memory_usage_freeze", "expected_value": "YES", "description": "Does Task Manager show application RAM consumption escalating until memory reaches 95-100% and freezes?", "is_intermediate": False}
        ],
        "explanation": "An unmanaged heap memory leak or unbounded background recursion is exhausting available committed virtual memory.",
        "solution": "1. Terminate the unresponsive process via Task Manager (Ctrl+Shift+Esc).\n2. Check for recent software patches or hotfixes addressing known memory leaks.\n3. Increase the Windows virtual memory paging file size on SSD.\n4. Close unnecessary resource-intensive background processes.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 8: Corrupted Cache or Preferences
    {
        "rule_id": "R-SOFT-008",
        "domain": "Software Troubleshooting",
        "diagnosis": "Corrupted Application Cache / User Profile Configuration",
        "conditions": [
            {"fact": "host_environment_compliant", "expected_value": "YES", "description": "Host environment compliant", "is_intermediate": True},
            {"fact": "execution_permissions_granted", "expected_value": "YES", "description": "Execution permissions granted", "is_intermediate": True},
            {"fact": "instant_crash_on_launch", "expected_value": "YES", "description": "Does the application crash or terminate immediately within 2 seconds of starting?", "is_intermediate": False},
            {"fact": "error_code_missing_dll", "expected_value": "NO", "description": "Does an error dialog specifically mention missing DLLs (e.g. VCRUNTIME140.dll, MSVCP140.dll)?", "is_intermediate": False}
        ],
        "explanation": "Cached serialized state or configuration files in AppData became corrupted, causing unhandled JSON/XML parser exceptions on startup.",
        "solution": "1. Press Win+R, navigate to '%APPDATA%' and '%LOCALAPPDATA%'.\n2. Locate the application's configuration folder and rename it with '.bak' extension.\n3. Relaunch the program to allow it to regenerate clean default preferences.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },

    # =========================================================================
    # DOMAIN 3: VEHICLE TROUBLESHOOTING (SAFETY CONSCIOUS)
    # =========================================================================
    # Intermediate Rule: Electrical System Powered
    {
        "rule_id": "R-VEH-INT-001",
        "domain": "Vehicle Troubleshooting",
        "intermediate_fact": "electrical_system_powered",
        "diagnosis": None,
        "conditions": [
            {"fact": "dashboard_lights_illuminate", "expected_value": "YES", "description": "Do the dashboard warning lights and instrument cluster illuminate when ignition is switched ON?", "is_intermediate": False},
            {"fact": "starter_rapid_clicking_sound", "expected_value": "NO", "description": "Do you hear a loud, rapid clicking chatter without the engine turning over?", "is_intermediate": False}
        ],
        "explanation": "The 12V automotive battery is providing adequate threshold voltage to power onboard electronic control modules.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Intermediate Rule: Cranking Subsystem Functional
    {
        "rule_id": "R-VEH-INT-002",
        "domain": "Vehicle Troubleshooting",
        "intermediate_fact": "cranking_subsystem_functional",
        "diagnosis": None,
        "conditions": [
            {"fact": "electrical_system_powered", "expected_value": "YES", "description": "Electrical system powered", "is_intermediate": True},
            {"fact": "starter_motor_cranks_engine", "expected_value": "YES", "description": "Does the starter motor vigorously rotate and crank the vehicle engine?", "is_intermediate": False}
        ],
        "explanation": "Starter solenoid, ignition switch circuit, and starter motor pinion gear mechanically engage the flywheel successfully.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Intermediate Rule: Severe Cooling Breach
    {
        "rule_id": "R-VEH-INT-003",
        "domain": "Vehicle Troubleshooting",
        "intermediate_fact": "cooling_system_compromised",
        "diagnosis": None,
        "conditions": [
            {"fact": "engine_overheating_gauge_in_red", "expected_value": "YES", "description": "Is the temperature gauge needle resting in the red warning zone or temperature warning lamp lit?", "is_intermediate": False},
            {"fact": "steam_escaping_from_hood", "expected_value": "YES", "description": "Is steam or boiling coolant vapor visibly escaping from underneath the engine hood?", "is_intermediate": False}
        ],
        "explanation": "The engine cooling system has suffered thermal runaway or catastrophic loss of pressurized coolant.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 1: Depleted 12V Battery
    {
        "rule_id": "R-VEH-001",
        "domain": "Vehicle Troubleshooting",
        "diagnosis": "Depleted or Discharged 12V Starter Battery",
        "conditions": [
            {"fact": "dashboard_lights_illuminate", "expected_value": "NO", "description": "Do the dashboard warning lights and instrument cluster illuminate when ignition is switched ON?", "is_intermediate": False}
        ],
        "explanation": "The lead-acid or AGM 12-volt battery terminal voltage has dropped below 10.5V due to parasite drain, age, or headlight discharge.",
        "solution": "1. Check battery terminals for white powdery corrosion and tighten loose clamps.\n2. Perform a safe jump-start using booster cables or a portable lithium jump pack following manual guidelines.\n3. If battery is over 4 years old, have a certified battery shop conduct a 100A load test.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 2: Weak Battery / Solenoid Chatter
    {
        "rule_id": "R-VEH-002",
        "domain": "Vehicle Troubleshooting",
        "diagnosis": "Low Battery Voltage Causing Starter Solenoid Chatter",
        "conditions": [
            {"fact": "dashboard_lights_illuminate", "expected_value": "YES", "description": "Do the dashboard warning lights and instrument cluster illuminate when ignition is switched ON?", "is_intermediate": False},
            {"fact": "starter_rapid_clicking_sound", "expected_value": "YES", "description": "Do you hear a loud, rapid clicking chatter without the engine turning over?", "is_intermediate": False}
        ],
        "explanation": "Battery has enough charge for low-current LED indicator lights, but voltage collapses immediately under 150A starter motor draw.",
        "solution": "1. Do not hold the ignition key down repeatedly to avoid burning the starter solenoid.\n2. Inspect ground wire connection between engine block and chassis.\n3. Jump-start the vehicle or recharge the 12V battery with a dedicated smart charger.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 3: Starter Motor Failure
    {
        "rule_id": "R-VEH-003",
        "domain": "Vehicle Troubleshooting",
        "diagnosis": "Faulty Starter Motor or Starter Relay Circuit",
        "conditions": [
            {"fact": "electrical_system_powered", "expected_value": "YES", "description": "Electrical system powered", "is_intermediate": True},
            {"fact": "starter_motor_cranks_engine", "expected_value": "NO", "description": "Does the starter motor vigorously rotate and crank the vehicle engine?", "is_intermediate": False}
        ],
        "explanation": "Battery voltage is confirmed healthy, but electrical current is not reaching or engaging the internal starter motor windings.",
        "solution": "1. Ensure the automatic transmission selector is firmly in PARK or neutral (clutch fully depressed for manual).\n2. Inspect the starter relay and fuse in the under-hood engine bay fuse box.\n3. Have a qualified automotive technician test the starter motor and solenoid wiring.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 4: Fuel Starvation
    {
        "rule_id": "R-VEH-004",
        "domain": "Vehicle Troubleshooting",
        "diagnosis": "Fuel Starvation or Depleted Fuel Tank",
        "conditions": [
            {"fact": "cranking_subsystem_functional", "expected_value": "YES", "description": "Cranking subsystem functional", "is_intermediate": True},
            {"fact": "fuel_level_sufficient", "expected_value": "NO", "description": "Does the fuel gauge or instrument display indicate at least 1/4 tank of fuel remaining?", "is_intermediate": False}
        ],
        "explanation": "Engine cranks with good compression and rotational speed, but cylinders lack combustible hydrocarbon fuel mixture.",
        "solution": "1. Add at least 5 to 10 liters of appropriate fuel to the tank.\n2. Switch ignition ON (without cranking) for 5 seconds three times to prime the electric fuel pump.\n3. Attempt to start the vehicle again.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 5: Severe Overheating / Radiator Failure
    {
        "rule_id": "R-VEH-005",
        "domain": "Vehicle Troubleshooting",
        "diagnosis": "CRITICAL: Severe Engine Thermal Overheating / Coolant Loss",
        "conditions": [
            {"fact": "cooling_system_compromised", "expected_value": "YES", "description": "Cooling system compromised", "is_intermediate": True}
        ],
        "explanation": "SAFETY HAZARD: The engine block has exceeded critical thermal operating limits. Continued operation causes blown cylinder head gaskets or warped engine blocks.",
        "solution": "1. SAFELY PULL OVER IMMEDIATELY and turn off the engine.\n2. WARNING: NEVER open the radiator pressure cap while the engine is hot (severe scalding steam danger).\n3. Allow engine to cool for at least 45 minutes.\n4. Call roadside assistance or a flatbed tow truck to a certified repair facility.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 6: Low Tyre Pressure
    {
        "rule_id": "R-VEH-006",
        "domain": "Vehicle Troubleshooting",
        "diagnosis": "Tyre Pressure Deflation / Slow Tread Puncture",
        "conditions": [
            {"fact": "tyre_pressure_warning_light_on", "expected_value": "YES", "description": "Is the TPMS (yellow horseshoe with exclamation point) warning indicator illuminated on the dash?", "is_intermediate": False},
            {"fact": "audible_tyre_air_hiss", "expected_value": "YES", "description": "Is there an audible air hiss or visible flat spot on any of the four tyres?", "is_intermediate": False}
        ],
        "explanation": "A pneumatic puncture from a road nail or compromised valve stem has caused pressure to drop below safe driving thresholds.",
        "solution": "1. Safely park on firm, level ground away from moving traffic.\n2. Do not drive on a flat tyre to avoid destroying the alloy rim and sidewall.\n3. Mount the spare emergency tyre using vehicle jack and wheel brace, or use a tyre sealant inflator kit.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 7: Brake Pad Wear
    {
        "rule_id": "R-VEH-007",
        "domain": "Vehicle Troubleshooting",
        "diagnosis": "Brake Friction Pad Material Wear / Acoustic Sensor Alert",
        "conditions": [
            {"fact": "brake_wear_indicator_squeal", "expected_value": "YES", "description": "Do you hear a loud, metallic high-pitched squealing sound when depressing the brake pedal?", "is_intermediate": False}
        ],
        "explanation": "The sacrificial metallic wear indicator tab is contacting the brake rotor, warning that pad lining thickness is below 2.5 mm.",
        "solution": "1. Avoid aggressive high-speed braking.\n2. Schedule an appointment with an authorized automotive brake specialist.\n3. Have front and rear brake pads and disc rotor thickness inspected and replaced promptly.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 8: Flashing Check Engine Light (Misfire)
    {
        "rule_id": "R-VEH-008",
        "domain": "Vehicle Troubleshooting",
        "diagnosis": "CRITICAL: Engine Cylinder Misfire Threatening Catalytic Converter",
        "conditions": [
            {"fact": "cranking_subsystem_functional", "expected_value": "YES", "description": "Cranking subsystem functional", "is_intermediate": True},
            {"fact": "check_engine_light_flashing", "expected_value": "YES", "description": "Is the Check Engine / Malfunction Indicator Lamp actively FLASHING rather than steady?", "is_intermediate": False}
        ],
        "explanation": "A flashing Check Engine light indicates severe raw fuel dumping unburned into the exhaust manifold, which can melt the catalytic converter or cause fires.",
        "solution": "1. Reduce speed immediately and avoid heavy throttle or towing.\n2. Park the vehicle safely as soon as feasible.\n3. Have the vehicle towed or scanned with an OBD-II diagnostic tool by a certified mechanic to read P0300-P0308 DTC trouble codes.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },

    # =========================================================================
    # DOMAIN 4: IOT & HARDWARE TROUBLESHOOTING
    # =========================================================================
    # Intermediate Rule: MCU Power Rail Healthy
    {
        "rule_id": "R-IOT-INT-001",
        "domain": "IoT & Hardware Troubleshooting",
        "intermediate_fact": "mcu_power_rail_healthy",
        "diagnosis": None,
        "conditions": [
            {"fact": "mcu_power_led_lit", "expected_value": "YES", "description": "Is the onboard Power LED (labeled PWR / 3V3 / 5V) steadily illuminated on the microcontroller?", "is_intermediate": False},
            {"fact": "supply_voltage_drops_under_load", "expected_value": "NO", "description": "Does the multimeter measure a voltage drop greater than 0.5V when Wi-Fi/BLE radio transmits?", "is_intermediate": False}
        ],
        "explanation": "The microcontroller development board is receiving regulated voltage within standard operating ripple tolerances.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Intermediate Rule: USB Interface Operational
    {
        "rule_id": "R-IOT-INT-002",
        "domain": "IoT & Hardware Troubleshooting",
        "intermediate_fact": "usb_serial_interface_operational",
        "diagnosis": None,
        "conditions": [
            {"fact": "mcu_power_rail_healthy", "expected_value": "YES", "description": "MCU power rail healthy", "is_intermediate": True},
            {"fact": "usb_port_recognized_in_os", "expected_value": "YES", "description": "Does the host computer OS register a valid USB COM / CDC-ACM serial port in Device Manager?", "is_intermediate": False}
        ],
        "explanation": "USB D+/D- differential data lines and the bridge IC (CP2102/CH340/FT232) are communicating with the host operating system.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Intermediate Rule: I2C Hardware Bus Intact
    {
        "rule_id": "R-IOT-INT-003",
        "domain": "IoT & Hardware Troubleshooting",
        "intermediate_fact": "i2c_bus_hardware_intact",
        "diagnosis": None,
        "conditions": [
            {"fact": "mcu_power_rail_healthy", "expected_value": "YES", "description": "MCU power rail healthy", "is_intermediate": True},
            {"fact": "pull_up_resistors_installed", "expected_value": "YES", "description": "Are dedicated 4.7kΩ pull-up resistors fitted between VCC and the I2C SDA/SCL lines?", "is_intermediate": False}
        ],
        "explanation": "Open-drain I2C serial data and clock lines have appropriate resistive bias to high-logic rail.",
        "solution": "N/A - Intermediate State",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 1: Total Board Power Deprivation
    {
        "rule_id": "R-IOT-001",
        "domain": "IoT & Hardware Troubleshooting",
        "diagnosis": "Total Board Power Deprivation / Open Circuit",
        "conditions": [
            {"fact": "mcu_power_led_lit", "expected_value": "NO", "description": "Is the onboard Power LED (labeled PWR / 3V3 / 5V) steadily illuminated on the microcontroller?", "is_intermediate": False}
        ],
        "explanation": "The development board is receiving zero input current through the USB VBUS or VIN header pins, or the onboard polyfuse has tripped.",
        "solution": "1. Replace the USB cable (many cheap cables are power-less or charge-only).\n2. Try plugging into a known-good direct USB port on the computer (avoid unpowered hubs).\n3. Check for physical short circuits between VCC and GND pins with a digital multimeter.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 2: Brownout Under RF Peak
    {
        "rule_id": "R-IOT-002",
        "domain": "IoT & Hardware Troubleshooting",
        "diagnosis": "Power Supply Brownout Under Radio Frequency Transmit Peak",
        "conditions": [
            {"fact": "mcu_power_led_lit", "expected_value": "YES", "description": "Is the onboard Power LED (labeled PWR / 3V3 / 5V) steadily illuminated on the microcontroller?", "is_intermediate": False},
            {"fact": "supply_voltage_drops_under_load", "expected_value": "YES", "description": "Does the multimeter measure a voltage drop greater than 0.5V when Wi-Fi/BLE radio transmits?", "is_intermediate": False}
        ],
        "explanation": "Wireless transmit pulses (ESP32/ESP8266 Wi-Fi spikes) demand up to 500mA instantaneously, collapsing weak LDO regulators and triggering BOR reset.",
        "solution": "1. Solder a 10µF to 100µF electrolytic or tantalum decoupling capacitor directly across 3.3V and GND.\n2. Power the microcontroller board with an external dedicated 5V 2A regulated power supply.\n3. Ensure USB power ports provide full 500mA-1A compliant power.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 3: Missing USB-to-UART Driver
    {
        "rule_id": "R-IOT-003",
        "domain": "IoT & Hardware Troubleshooting",
        "diagnosis": "Missing USB-to-UART Bridge Driver (CH340 / CP2102)",
        "conditions": [
            {"fact": "mcu_power_led_lit", "expected_value": "YES", "description": "Is the onboard Power LED (labeled PWR / 3V3 / 5V) steadily illuminated on the microcontroller?", "is_intermediate": False},
            {"fact": "usb_port_recognized_in_os", "expected_value": "NO", "description": "Does the host computer OS register a valid USB COM / CDC-ACM serial port in Device Manager?", "is_intermediate": False}
        ],
        "explanation": "The computer detects unknown hardware but cannot bind a VCP virtual COM port driver to the USB UART bridge chipset.",
        "solution": "1. Identify the small rectangular IC near the USB port (e.g. CH340G, CP2102, or FT232RL).\n2. Download and install the official manufacturer driver installer.\n3. Restart the Arduino IDE, VSCode/PlatformIO, or terminal monitor after driver setup.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 4: Bootloader Sync / Flash Timeout
    {
        "rule_id": "R-IOT-004",
        "domain": "IoT & Hardware Troubleshooting",
        "diagnosis": "Microcontroller Bootloader Synchronization Failure",
        "conditions": [
            {"fact": "usb_serial_interface_operational", "expected_value": "YES", "description": "USB serial interface operational", "is_intermediate": True},
            {"fact": "firmware_upload_timed_out", "expected_value": "YES", "description": "Does the IDE compiler/uploader report 'Failed to connect' or packet header sync timeout?", "is_intermediate": False},
            {"fact": "boot_button_pressed_during_flash", "expected_value": "NO", "description": "Did you manually press and hold the GPIO0 / BOOT button when the flashing tool initiated connection?", "is_intermediate": False}
        ],
        "explanation": "The auto-reset circuit (DTR/RTS transistor network) failed to latch GPIO0 LOW to enter ROM bootloader download mode.",
        "solution": "1. Hold down the onboard 'BOOT' (GPIO0) button as soon as 'Connecting...' appears in terminal.\n2. Release the button only after the progress percentage starts advancing.\n3. Solder a 1µF capacitor between the EN/RESET pin and GND to automate auto-reset timing.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 5: I2C Missing Pull-Ups
    {
        "rule_id": "R-IOT-005",
        "domain": "IoT & Hardware Troubleshooting",
        "diagnosis": "Floating I2C Bus / Missing Bus Pull-Up Resistors",
        "conditions": [
            {"fact": "mcu_power_rail_healthy", "expected_value": "YES", "description": "MCU power rail healthy", "is_intermediate": True},
            {"fact": "pull_up_resistors_installed", "expected_value": "NO", "description": "Are dedicated 4.7kΩ pull-up resistors fitted between VCC and the I2C SDA/SCL lines?", "is_intermediate": False},
            {"fact": "i2c_bus_scanner_detects_address", "expected_value": "NO", "description": "Does an I2C bus scanner script detect the sensor's hexadecimal slave address?", "is_intermediate": False}
        ],
        "explanation": "I2C is an open-drain architecture. Without pull-up resistors, the signal lines cannot reliably return to HIGH logic state.",
        "solution": "1. Place two 4.7kΩ (or 10kΩ) resistors from the SDA and SCL lines to the 3.3V power rail.\n2. Keep I2C hookup wire leads short (under 20 cm) to minimize capacitive bus loading.\n3. Run a known I2C scanner sketch to confirm acknowledgment (ACK).",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 6: Logic Voltage Clamping Mismatch
    {
        "rule_id": "R-IOT-006",
        "domain": "IoT & Hardware Troubleshooting",
        "diagnosis": "Logic Voltage Level Clamping / Incompatible Thresholds",
        "conditions": [
            {"fact": "mcu_power_rail_healthy", "expected_value": "YES", "description": "MCU power rail healthy", "is_intermediate": True},
            {"fact": "logic_voltage_level_matched", "expected_value": "NO", "description": "Are both the microcontroller and the peripheral sensor running at compatible logic levels (e.g. 3.3V vs 5V)?", "is_intermediate": False}
        ],
        "explanation": "Connecting a 5V sensor directly to 3.3V non-5V-tolerant MCU GPIO pins triggers ESD protection diodes, distorting signals or destroying silicon.",
        "solution": "1. Insert a bi-directional BSS138 MOSFET-based logic level shifter module.\n2. Never connect raw 5V TTL outputs directly to 3.3V microcontroller inputs.\n3. Verify jumper selection on sensors with selectable 3.3V/5V LDO regulators.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 7: Damaged Sensor / Wiring Reversal
    {
        "rule_id": "R-IOT-007",
        "domain": "IoT & Hardware Troubleshooting",
        "diagnosis": "Sensor Element Failure or Wiring Signal Inversion",
        "conditions": [
            {"fact": "i2c_bus_hardware_intact", "expected_value": "YES", "description": "I2C bus hardware intact", "is_intermediate": True},
            {"fact": "sensor_readings_out_of_range", "expected_value": "YES", "description": "Are telemetry sensor readings outputting extreme invalid constants (such as -127°C, 65535, or NaN)?", "is_intermediate": False}
        ],
        "explanation": "The hardware bus responds to address polling, but internal register reads return invalid fixed bytes due to damaged transducer elements or swapped data lines.",
        "solution": "1. Double-check pinout markings: ensure SDA is connected to SDA and SCL to SCL.\n2. Inspect sensor module for signs of overheating or burnt traces.\n3. Test with a secondary spare sensor module to isolate silicon failure.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    },
    # Diagnosis 8: Unfiltered ADC Line Noise
    {
        "rule_id": "R-IOT-008",
        "domain": "IoT & Hardware Troubleshooting",
        "diagnosis": "Analog-to-Digital Reference Noise / Unfiltered Line EMI",
        "conditions": [
            {"fact": "mcu_power_rail_healthy", "expected_value": "YES", "description": "MCU power rail healthy", "is_intermediate": True},
            {"fact": "analog_reading_has_excessive_noise", "expected_value": "YES", "description": "Do analog ADC samples swing erratically (>10% variance) without any physical environmental change?", "is_intermediate": False}
        ],
        "explanation": "Switching power supply ripple and electromagnetic interference are coupling into the high-impedance ADC sample-and-hold capacitor.",
        "solution": "1. Add a 100nF ceramic capacitor in parallel across the analog input pin and GND.\n2. Implement a software exponential moving average (EMA) or median filter on raw samples.\n3. Avoid routing high-current PWM motor traces parallel to analog sensing wires.",
        "approval_status": "APPROVED",
        "author": "System Baseline"
    }
]

# Write baseline knowledge base
with open(DATA_DIR / "knowledge_base_baseline.json", "w", encoding="utf-8") as f:
    json.dump({"version": "1.0.0", "rules": BASELINE_RULES}, f, indent=2)

# Copy baseline to active knowledge base
with open(DATA_DIR / "knowledge_base.json", "w", encoding="utf-8") as f:
    json.dump({"version": "1.0.0", "rules": BASELINE_RULES}, f, indent=2)

print(f"Successfully generated baseline KB with {len(BASELINE_RULES)} rules.")
