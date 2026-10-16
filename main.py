import json

from common.enumerators.device_type import DeviceType
from common.latex.document_generator import DocumentGenerator
from common.service_interactions.mikrotik.mikrotik_control_dhcp_server import MikrotikControlDhcpServer
from common.service_interactions.mikrotik.mikrotik_control_firewall_ipv4 import MikrotikControlFirewallIpv4
from common.service_interactions.mikrotik.mikrotik_control_vlan import MikrotikControlVlan
from common.service_interactions.opnsense.opnsense_control_vlan import OpnsenseControlVlan
from common.service_interactions.opnsense_device import OPNSenseDevice
from common.service_interactions.mikrotik.mikrotik_control_capsman import MikrotikControlCapsman
from common.utilities.configuration import Configuration
from common.service_interactions.mikrotik_device import MikrotikDevice


def gather_network_information(network_devices) -> dict:
    network_spec = {
        "VLANs": {},
        "Firewall": {},
        "DHCP": {},
        "CAPsMAN": {},
    }

    for device in network_devices:
        if "VlanController" in device.DEVICE_CONFIG["Roles"]:
            if device.DEVICE_CONFIG["Type"] == "MikroTIK":
                network_spec["VLANs"] = MikrotikControlVlan(device).build_payload()
            elif device.DEVICE_CONFIG["Type"] == "OPNSense":
                network_spec["VLANs"] = {"": OpnsenseControlVlan(device).build_payload()}

        if "Firewall" in device.DEVICE_CONFIG["Roles"]:
            if device.DEVICE_CONFIG["Type"] == "MikroTIK":
                network_spec["Firewall"] = MikrotikControlFirewallIpv4(device).build_payload()
            else:
                raise Exception(f"Firewall is not implemented for {device.DEVICE_CONFIG['Type']} yet.")

        if "DhcpServer" in device.DEVICE_CONFIG["Roles"]:
            if device.DEVICE_CONFIG["Type"] == "MikroTIK":
                network_spec["DHCP"] = MikrotikControlDhcpServer(device).build_payload()
            else:
                raise Exception(f"DhcpServer is not implemented for {device.DEVICE_CONFIG['Type']} yet.")

        if "CAPsMAN" in device.DEVICE_CONFIG["Roles"]:
            if device.DEVICE_CONFIG["Type"] != "MikroTIK":
                raise Exception("CAPsMAN is a MikroTIK-only feature")
            network_spec["CAPsMAN"] = MikrotikControlCapsman(device).build_payload()

    return network_spec


def generate_document(network_spec: dict) -> None:
    with open("cache/network_spec.json", "w") as f:
        f.write(
            json.dumps(network_spec, indent=4)
        )


def main() -> None:
    Configuration.load("config.yaml")

    devices_config = Configuration.get("NetworkDevices")

    network_devices: list[
        MikrotikDevice
        |OPNSenseDevice
    ] = []

    print("Connecting to devices...")

    try:
        for device_name, device_details in devices_config.items():
            device_type = device_details["Type"]

            if device_type == DeviceType.MikroTIK.value:
                device = MikrotikDevice(device_name)
            elif device_type == DeviceType.OPNSense.value:
                device = OPNSenseDevice(device_name)
            else:
                print(
                    f"    {device_name} - UNSUPPORTED ({device_type})"
                )
                continue

            print(f"    {device_name}", end="")

            if not device.connect():
                raise RuntimeError(
                    f"Failed to connect to {device_name}"
                )

            if not device.verify_name(device_name):
                device.disconnect()
                raise RuntimeError(
                    f"Device {device_name} is not the expected device"
                )

            network_devices.append(device)

            print(" - CONNECTED")

        print("Collecting network information...")
        network_spec = gather_network_information(network_devices)

        print("Generating document...")
        generate_document(network_spec)

    finally:
        print("Disconnecting from devices...")

        for device in network_devices:
            device.disconnect()

        print("Done :3")


if __name__ == "__main__":
    main()
