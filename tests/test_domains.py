"""Unit tests validating each of the four troubleshooting domains."""

import pytest
from src.inference_engine import BackwardChainingEngine
from config import STATUS_CONFIRMED


def test_network_domain_scenarios(baseline_kb):
    """Verifies that Network Troubleshooting diagnoses work through backward chaining."""
    engine = BackwardChainingEngine(baseline_kb)

    # Scenario 1: Wi-Fi adapter disabled
    res1 = engine.diagnose_domain("Network Troubleshooting", {"wifi_adapter_enabled": "NO"})
    assert res1.status == STATUS_CONFIRMED
    assert "Wi-Fi Adapter Disabled" in res1.primary_diagnosis

    # Scenario 2: Captive portal
    res2 = engine.diagnose_domain("Network Troubleshooting", {
        "wifi_adapter_enabled": "YES",
        "local_network_connected": "YES",
        "router_gateway_ping_success": "YES",
        "public_ip_ping_success": "NO",
        "captive_portal_detected": "YES"
    })
    assert res2.status == STATUS_CONFIRMED
    assert "Captive Portal" in res2.primary_diagnosis


def test_software_domain_scenarios(baseline_kb):
    """Verifies that Software Troubleshooting diagnoses work through backward chaining."""
    engine = BackwardChainingEngine(baseline_kb)

    # Scenario 1: OS Incompatible
    res1 = engine.diagnose_domain("Software Troubleshooting", {"system_meets_minimum_os_version": "NO"})
    assert res1.status == STATUS_CONFIRMED
    assert "Operating System" in res1.primary_diagnosis

    # Scenario 2: Missing DLL runtimes
    res2 = engine.diagnose_domain("Software Troubleshooting", {
        "system_meets_minimum_os_version": "YES",
        "available_disk_space_sufficient": "YES",
        "visual_c_runtimes_installed": "NO",
        "error_code_missing_dll": "YES"
    })
    assert res2.status == STATUS_CONFIRMED
    assert "Missing Dynamic Link Libraries" in res2.primary_diagnosis


def test_vehicle_domain_scenarios(baseline_kb):
    """Verifies that Vehicle Troubleshooting diagnoses work with safety-conscious advice."""
    engine = BackwardChainingEngine(baseline_kb)

    # Scenario 1: Dead battery
    res1 = engine.diagnose_domain("Vehicle Troubleshooting", {"dashboard_lights_illuminate": "NO"})
    assert res1.status == STATUS_CONFIRMED
    assert "Battery" in res1.primary_diagnosis

    # Scenario 2: Severe Overheating (Safety Alert)
    res2 = engine.diagnose_domain("Vehicle Troubleshooting", {
        "engine_overheating_gauge_in_red": "YES",
        "steam_escaping_from_hood": "YES"
    })
    assert res2.status == STATUS_CONFIRMED
    assert "CRITICAL" in res2.primary_diagnosis
    assert "NEVER open the radiator pressure cap" in res2.primary_solution


def test_iot_domain_scenarios(baseline_kb):
    """Verifies that IoT & Hardware Troubleshooting diagnoses work through backward chaining."""
    engine = BackwardChainingEngine(baseline_kb)

    # Scenario 1: Unpowered board
    res1 = engine.diagnose_domain("IoT & Hardware Troubleshooting", {"mcu_power_led_lit": "NO"})
    assert res1.status == STATUS_CONFIRMED
    assert "Power Deprivation" in res1.primary_diagnosis

    # Scenario 2: Missing I2C pullups
    res2 = engine.diagnose_domain("IoT & Hardware Troubleshooting", {
        "mcu_power_led_lit": "YES",
        "supply_voltage_drops_under_load": "NO",
        "pull_up_resistors_installed": "NO",
        "i2c_bus_scanner_detects_address": "NO"
    })
    assert res2.status == STATUS_CONFIRMED
    assert "Floating I2C Bus" in res2.primary_diagnosis
