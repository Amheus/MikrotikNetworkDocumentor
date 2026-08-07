import json

from common.enumerators.device_type import DeviceType
from common.service_interactions.opnsense.opnsense_vlan_control import OPNSenseVLANControl
from common.service_interactions.opnsense_device import OPNSenseDevice
from common.service_interactions.mikrotik.mikrotik_capsman_control import CAPsMAN
from common.utilities.configuration import Configuration
from common.service_interactions.mikrotik_device import MikrotikDevice


def go(network_devices) -> None:
    network_spec = {
        "VLANs": [],
        "CAPsMAN": {},
    }

    for device in network_devices:
        if "VlanController" in device.DEVICE_CONFIG["Roles"]:
            if device.DEVICE_CONFIG["Type"] == "MikroTIK":
                raise NotImplementedError("Mikrotik VLANs not yet implemented")
            elif device.DEVICE_CONFIG["Type"] == "OPNSense":
                network_spec["VLANs"] = OPNSenseVLANControl(device).get_vlan_config()

        if "CAPsMAN" in device.DEVICE_CONFIG["Roles"]:
            if device.DEVICE_CONFIG["Type"] != "MikroTIK":
                raise Exception("CAPsMAN is a MikroTIK-only feature")
            network_spec["CAPsMAN"] = CAPsMAN(device).build_payload()



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
        go(network_devices)

    finally:
        print("Disconnecting from devices...")

        for device in network_devices:
            device.disconnect()

        print("Done :3")


if __name__ == "__main__":
    main()